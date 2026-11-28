"""问题3：复用问题1的逐周期校准和直射波抑制，进行墙体/金属目标三维成像。"""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from channel_calibration import (
    C0,
    FS,
    NP,
    aligned_profile,
    apply_calibration,
    geometry,
    read_dat_cycles,
)
from range_measurement import (
    analytic_signal,
    build_direct_templates,
    fourier_resample,
    locate_direct,
    make_template_bank,
    shift_rows,
    stabilize_direct_centers,
    suppress_direct,
)

WORKSPACE = Path(__file__).resolve().parent
IMAGING_ROOT = Path(r"C:\Users\wangq\Desktop\2027年电子科大美赛模拟赛竞赛题目\竞赛题目\A 题：单发多收下的雷达信号处理及成像问题\附件\附件3-成像数据")
RANGING_ROOT = Path(r"C:\Users\wangq\Desktop\2027年电子科大美赛模拟赛竞赛题目\竞赛题目\A 题：单发多收下的雷达信号处理及成像问题\附件\附件2-测距数据")
CALIBRATION = WORKSPACE / "calibration_period_output" / "channel_calibration.npz"
EPS = 1e-12


def discover_scans(scene_dir: Path):
    grouped = {}
    for path in scene_dir.glob("*.dat"):
        match = re.fullmatch(r"(.+_\d+)_([0-7])\.dat", path.name)
        if match:
            grouped.setdefault(match.group(1), {})[int(match.group(2))] = path
    complete = []
    for prefix, rows in sorted(grouped.items()):
        if len(rows) == 8:
            complete.append((prefix, rows))
        else:
            print(f"跳过不完整测点 {prefix}: 只有 {len(rows)}/8 行")
    return complete


def load_scan(rows):
    row_data = []
    for row in range(8):
        cycles, _ = read_dat_cycles(rows[row])
        row_data.append(cycles.mean(axis=0))
    return np.concatenate(row_data, axis=0)


def voxel_grid(x_range, y_range, z_range, step_cm):
    axes = [np.arange(start, stop + step_cm / 2, step_cm) for start, stop in (x_range, y_range, z_range)]
    mesh = np.meshgrid(*axes, indexing="ij")
    voxels = np.stack(mesh, axis=-1).reshape(-1, 3) / 100.0
    return axes, voxels


def prepare_profiles(scene_dir, scans, correction, rho_m, valid, templates):
    prepared = []
    for prefix, rows in scans:
        measured = load_scan(rows)
        calibrated = apply_calibration(measured, correction, valid)
        original = aligned_profile(calibrated, rho_m)
        center, _ = locate_direct(original, templates, valid)
        prepared.append((prefix, original, center))
    stabilized = stabilize_direct_centers(np.array([item[2] for item in prepared]))
    return [(prefix, original, center) for (prefix, original, _), center in zip(prepared, stabilized)]


def backproject_scene(scene, scene_dir, scans, correction, quality, geometry_data,
                      templates, template_bank, delay_grid, args):
    rows, slots, cols, x_cm, z_cm, rho_m, valid, labels = geometry_data
    if scene == "wall":
        scan_x_cm = np.array([-20 + 5 * index for index in range(len(scans))], dtype=float)
        ranges = ((-20, 140), (0, 250), (20, 80))
    else:
        scan_x_cm = np.array([5 * index for index in range(len(scans))], dtype=float)
        ranges = ((0, 130), (0, 250), (20, 80))
    if args.max_scans:
        scans = scans[:args.max_scans]
        scan_x_cm = scan_x_cm[:args.max_scans]
    axes, voxels = voxel_grid(*ranges, args.grid_step_cm)
    shape = tuple(len(axis) for axis in axes)
    raw_volume = np.zeros(voxels.shape[0])
    enhanced_volume = np.zeros(voxels.shape[0])
    incoherent_raw_volume = np.zeros(voxels.shape[0])
    incoherent_enhanced_volume = np.zeros(voxels.shape[0])
    normalization = np.zeros(voxels.shape[0])

    prepared = prepare_profiles(scene_dir, scans, correction, rho_m, valid, templates)
    receiver_x_local = (x_cm[valid] - 24.5) / 100.0
    receiver_z = z_cm[valid] / 100.0
    rho_valid = rho_m[valid]
    up = args.upsample_factor

    for scan_index, ((prefix, original, center), scan_x) in enumerate(zip(prepared, scan_x_cm)):
        profile = shift_rows(original, -center)
        residual, details = suppress_direct(
            profile, templates, valid, template_bank, delay_grid,
            args.direct_halfwidth, args.fit_halfwidth,
        )
        interpolated = fourier_resample(residual[valid], up)
        analytic = analytic_signal(interpolated)
        weights = np.maximum(quality, EPS) / details["direct_scale"]
        weights /= np.sum(weights)
        tx = np.array([scan_x / 100.0, 0.0, 0.545])
        receiver_x = scan_x / 100.0 + receiver_x_local

        for start in range(0, voxels.shape[0], args.chunk_size):
            stop = min(start + args.chunk_size, voxels.shape[0])
            points = voxels[start:stop]
            tx_distance = np.linalg.norm(points - tx, axis=1)
            coherent_raw = np.zeros(stop - start, dtype=complex)
            coherent_enhanced = np.zeros(stop - start, dtype=complex)
            incoherent_raw = np.zeros(stop - start)
            incoherent_enhanced = np.zeros(stop - start)
            norm_chunk = np.zeros(stop - start)
            for channel in range(int(valid.sum())):
                receiver = np.array([receiver_x[channel], 0.0, receiver_z[channel]])
                rx_distance = np.linalg.norm(points - receiver, axis=1)
                total_path = tx_distance + rx_distance
                positions = (total_path - rho_valid[channel]) * FS * up / C0
                base = np.floor(positions).astype(int)
                fraction = positions - base
                base = np.clip(base, 0, analytic.shape[1] - 2)
                samples = (
                    analytic[channel, base] * (1 - fraction)
                    + analytic[channel, base + 1] * fraction
                )
                path_gain = np.clip(total_path, 0.25, 5.0) ** args.gain_exponent
                coherent_raw += weights[channel] * samples
                coherent_enhanced += weights[channel] * path_gain * samples
                incoherent_raw += weights[channel] * np.abs(samples) ** 2
                incoherent_enhanced += weights[channel] * np.abs(path_gain * samples) ** 2
                norm_chunk += weights[channel]
            raw_volume[start:stop] += np.abs(coherent_raw) ** 2
            enhanced_volume[start:stop] += np.abs(coherent_enhanced) ** 2
            incoherent_raw_volume[start:stop] += incoherent_raw
            incoherent_enhanced_volume[start:stop] += incoherent_enhanced
            normalization[start:stop] += norm_chunk
        print(
            f"{scene} {scan_index + 1}/{len(prepared)} {prefix}: "
            f"direct={center:.2f}, suppression={details['suppression_db']:.2f} dB",
            flush=True,
        )

    normalization = np.maximum(normalization, EPS)
    result = {
        "axes": axes,
        "raw": (raw_volume / normalization).reshape(shape),
        "enhanced": (enhanced_volume / normalization).reshape(shape),
        "incoherent_raw": (incoherent_raw_volume / normalization).reshape(shape),
        "incoherent_enhanced": (incoherent_enhanced_volume / normalization).reshape(shape),
        "scan_x_cm": scan_x_cm,
        "ranges": ranges,
    }
    if scene == "metal":
        result["localized"] = localize_metal(result["enhanced"])
    return result


def localize_metal(volume):
    """扣除沿 x 方向延展的墙面背景，保留局部金属目标。"""
    background = np.median(volume, axis=0, keepdims=True)
    localized = np.maximum(volume - background, 0.0)
    smoothed = localized.copy()
    counts = np.ones_like(localized)
    for axis in range(3):
        for direction in (-1, 1):
            shifted = np.roll(localized, direction, axis=axis)
            if direction == 1:
                index = [slice(None)] * 3
                index[axis] = 0
                shifted[tuple(index)] = 0
            else:
                index = [slice(None)] * 3
                index[axis] = -1
                shifted[tuple(index)] = 0
            smoothed += shifted
            counts += 1
    return smoothed / counts


def save_projections(scene, result, output_dir, components=None):
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    axes = result["axes"]
    panels = [
        ("raw", "扫描内相干，未加路径增益"),
        ("enhanced", "扫描内相干 + 路径增益"),
        ("incoherent_enhanced", "全非相干 + 路径增益"),
    ]
    if scene == "metal":
        panels.append(("localized", "局部目标增强"))
    fig, image_axes = plt.subplots(len(panels), 3, figsize=(15, 4.7 * len(panels)))
    if len(panels) == 1:
        image_axes = image_axes[None, :]
    for row, (key, title) in enumerate(panels):
        volume = result[key]
        db = 10 * np.log10(np.maximum(volume, EPS) / (np.max(volume) + EPS) + EPS)
        projections = [
            (np.max(db, axis=2).T, (axes[0][0], axes[0][-1], axes[1][0], axes[1][-1]), "x / cm", "y / cm", "x-y 最大投影"),
            (np.max(db, axis=1).T, (axes[0][0], axes[0][-1], axes[2][0], axes[2][-1]), "x / cm", "z / cm", "x-z 最大投影"),
            (np.max(db, axis=0).T, (axes[1][0], axes[1][-1], axes[2][0], axes[2][-1]), "y / cm", "z / cm", "y-z 最大投影"),
        ]
        for column, (image, extent, xlabel, ylabel, subtitle) in enumerate(projections):
            axis = image_axes[row, column]
            plotted = axis.imshow(image, origin="lower", extent=extent, aspect="auto", cmap="inferno", vmin=-35, vmax=0)
            axis.set_title(f"{title}：{subtitle}")
            axis.set_xlabel(xlabel)
            axis.set_ylabel(ylabel)
            if components and row > 0:
                for component in components:
                    x, y, z = component["center_cm"]
                    coordinates = ((x, y), (x, z), (y, z))[column]
                    axis.scatter(*coordinates, marker="+", s=90, linewidths=1.5, color="cyan")
            fig.colorbar(plotted, ax=axis, label="相对强度 / dB")
    fig.tight_layout()
    fig.savefig(output_dir / f"{scene}_projections.png", dpi=170)
    plt.close(fig)


def smooth_1d(values, width=5):
    kernel = np.hamming(width)
    kernel /= np.sum(kernel)
    return np.convolve(np.pad(values, width // 2, mode="reflect"), kernel, mode="valid")


def analyze_wall(result):
    axes = result["axes"]
    volume = result["enhanced"]
    profile = smooth_1d(np.sum(volume, axis=(0, 2)))
    candidates = np.argsort(profile)[::-1]
    selected = []
    for index in candidates:
        if axes[1][index] < 10:
            continue
        if all(abs(axes[1][index] - axes[1][other]) >= 12 for other in selected):
            selected.append(int(index))
        if len(selected) == 2:
            break
    selected.sort(key=lambda index: axes[1][index])
    estimates = []
    for name, index in zip(("wall_A", "wall_B"), selected):
        halfwidth = max(1, int(round(6 / (axes[1][1] - axes[1][0]))))
        slab = volume[:, max(0, index - halfwidth):index + halfwidth + 1, :].max(axis=1)
        mask = slab >= 0.5 * np.max(slab)
        xx, zz = np.meshgrid(axes[0], axes[2], indexing="ij")
        estimates.append({
            "wall": name,
            "y_peak_cm": float(axes[1][index]),
            "x_min_cm": float(np.min(xx[mask])),
            "x_max_cm": float(np.max(xx[mask])),
            "z_min_cm": float(np.min(zz[mask])),
            "z_max_cm": float(np.max(zz[mask])),
            "profile_strength": float(profile[index]),
        })
    if len(estimates) == 2:
        front_y = estimates[0]["y_peak_cm"]
        back_y = estimates[1]["y_peak_cm"]
        interface = 0.5 * ((front_y + 10.5) + (back_y - 35.0))
        for estimate in estimates:
            estimate["interface_y_cm"] = float(interface)
            estimate["outer_surface_separation_cm"] = float(back_y - front_y)
    return estimates, profile


def connected_components(volume, axes):
    positive = volume[volume > 0]
    if not positive.size:
        return []
    threshold = np.quantile(positive, 0.985)
    coordinates = np.argwhere(volume >= threshold)
    if len(coordinates) > 6000:
        values = volume[tuple(coordinates.T)]
        coordinates = coordinates[np.argsort(values)[-6000:]]
        coordinates = coordinates[np.lexsort(coordinates.T[::-1])]
    index_map = np.full(volume.shape, -1, dtype=int)
    index_map[tuple(coordinates.T)] = np.arange(len(coordinates))
    parent = np.arange(len(coordinates))

    def find(index):
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    def union(left, right):
        left_root, right_root = find(left), find(right)
        if left_root != right_root:
            parent[right_root] = left_root

    offsets = [(a, b, c) for a in (-1, 0, 1) for b in (-1, 0, 1) for c in (-1, 0, 1) if (a, b, c) != (0, 0, 0)]
    for index, coordinate in enumerate(coordinates):
        for offset in offsets:
            neighbor = coordinate + offset
            if np.any(neighbor < 0) or np.any(neighbor >= volume.shape):
                continue
            other = index_map[tuple(neighbor)]
            if 0 <= other < index:
                union(index, other)

    groups = {}
    for index in range(len(coordinates)):
        groups.setdefault(find(index), []).append(index)
    components = []
    for indices in groups.values():
        indices = np.asarray(indices)
        if len(indices) < 2:
            continue
        points_index = coordinates[indices]
        points_cm = np.column_stack([axes[axis][points_index[:, axis]] for axis in range(3)])
        values = volume[tuple(points_index.T)]
        weight = values + EPS
        components.append({
            "center_cm": np.sum(points_cm * weight[:, None], axis=0) / np.sum(weight),
            "bbox_min_cm": np.min(points_cm, axis=0),
            "bbox_max_cm": np.max(points_cm, axis=0),
            "peak_cm": points_cm[int(np.argmax(values))],
            "voxel_count": len(indices),
            "peak": float(np.max(values)),
            "energy": float(np.sum(values)),
        })
    components.sort(key=lambda item: item["energy"], reverse=True)
    selected = []
    for component in components:
        if all(np.linalg.norm(component["center_cm"] - old["center_cm"]) >= 15 for old in selected):
            selected.append(component)
        if len(selected) == 2:
            break
    return selected


def save_scene_outputs(scene, result, output_dir):
    payload = {
        "x_cm": result["axes"][0], "y_cm": result["axes"][1], "z_cm": result["axes"][2],
        "raw_intensity": result["raw"], "enhanced_intensity": result["enhanced"],
        "incoherent_raw_intensity": result["incoherent_raw"],
        "incoherent_enhanced_intensity": result["incoherent_enhanced"],
        "scan_x_cm": result["scan_x_cm"],
    }
    if scene == "metal":
        components = connected_components(result["localized"], result["axes"])
        payload["localized_intensity"] = result["localized"]
        rows = []
        target_labels = {}
        if len(components) == 2:
            by_height = sorted(
                components,
                key=lambda item: item["bbox_max_cm"][2] - item["bbox_min_cm"][2],
                reverse=True,
            )
            target_labels[id(by_height[0])] = "metal_cylinder"
            target_labels[id(by_height[1])] = "metal_shovel"
        for rank, component in enumerate(components, 1):
            row = {"target": target_labels.get(id(component), f"localized_target_{rank}"), "voxel_count": component["voxel_count"], "energy": component["energy"]}
            for axis, value in zip("xyz", component["center_cm"]):
                row[f"center_{axis}_cm"] = float(value)
            for axis, value in zip("xyz", component["peak_cm"]):
                row[f"peak_{axis}_cm"] = float(value)
            for axis, value in zip("xyz", component["bbox_min_cm"]):
                row[f"bbox_min_{axis}_cm"] = float(value)
            for axis, value in zip("xyz", component["bbox_max_cm"]):
                row[f"bbox_max_{axis}_cm"] = float(value)
            rows.append(row)
        with (output_dir / "metal_position_estimates.csv").open("w", newline="", encoding="utf-8-sig") as file:
            writer = csv.DictWriter(file, fieldnames=list(rows[0]) if rows else ["target"])
            writer.writeheader()
            writer.writerows(rows)
        summary = rows
    else:
        estimates, profile = analyze_wall(result)
        with (output_dir / "wall_position_estimates.csv").open("w", newline="", encoding="utf-8-sig") as file:
            writer = csv.DictWriter(file, fieldnames=list(estimates[0]))
            writer.writeheader()
            writer.writerows(estimates)
        payload["y_projection_profile"] = profile
        summary = estimates
        components = None
    np.savez_compressed(output_dir / f"{scene}_volume.npz", **payload)
    save_projections(scene, result, output_dir, components)
    return summary


def parse_arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--imaging-root", type=Path, default=IMAGING_ROOT)
    parser.add_argument("--ranging-root", type=Path, default=RANGING_ROOT)
    parser.add_argument("--calibration", type=Path, default=CALIBRATION)
    parser.add_argument("--output-dir", type=Path, default=WORKSPACE / "imaging_output")
    parser.add_argument("--scene", choices=("both", "wall", "metal"), default="both")
    parser.add_argument("--grid-step-cm", type=float, default=2.0)
    parser.add_argument("--gain-exponent", type=float, default=1.0)
    parser.add_argument("--upsample-factor", type=int, default=2)
    parser.add_argument("--chunk-size", type=int, default=8192)
    parser.add_argument("--direct-halfwidth", type=int, default=5)
    parser.add_argument("--fit-halfwidth", type=int, default=3)
    parser.add_argument("--max-scans", type=int, default=0, help="仅调试用；0 表示全部测点")
    return parser.parse_args()


def main():
    args = parse_arguments()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    geometry_data = geometry()
    rho_m, valid = geometry_data[5], geometry_data[6]
    calibration = np.load(args.calibration)
    correction = calibration["complex_correction"]
    quality = calibration["quality_score"]
    templates, _, _ = build_direct_templates(
        args.ranging_root, correction, rho_m, valid, args.direct_halfwidth,
    )
    delay_grid = np.arange(-0.8, 0.8001, 0.05)
    template_bank = make_template_bank(templates, valid, delay_grid)

    scenes = []
    if args.scene in ("both", "wall"):
        scenes.append(("wall", "墙体"))
    if args.scene in ("both", "metal"):
        scenes.append(("metal", "金属柱和金属铲"))
    summary = {}
    for scene, folder in scenes:
        scans = discover_scans(args.imaging_root / folder)
        print(f"{scene}: {len(scans)} 个完整测点")
        result = backproject_scene(
            scene, args.imaging_root / folder, scans, correction, quality,
            geometry_data, templates, template_bank, delay_grid, args,
        )
        summary[scene] = save_scene_outputs(scene, result, args.output_dir)
        print(scene, json.dumps(summary[scene], ensure_ascii=False))
    with (args.output_dir / "imaging_summary.json").open("w", encoding="utf-8") as file:
        json.dump(summary, file, ensure_ascii=False, indent=2)
    print(f"结果已保存到: {args.output_dir}")


if __name__ == "__main__":
    main()
