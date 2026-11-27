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
    C0 as C,
    FS,
    NP,
    aligned_profile,
    apply_calibration,
    circular_offset,
    consensus_center,
    discover_groups,
    geometry,
    hann_gate,
    load_group,
)

ROOT = Path(r"C:\Users\wangq\Desktop\2027年电子科大美赛模拟赛竞赛题目\竞赛题目\A 题：单发多收下的雷达信号处理及成像问题\附件\附件2-测距数据")
CALIBRATION = Path(__file__).with_name("calibration_output") / "channel_calibration.npz"
EPS = 1e-12


def analytic_signal(values: np.ndarray) -> np.ndarray:
    """用 FFT 构造解析信号，避免额外依赖 SciPy。"""
    count = values.shape[-1]
    multiplier = np.zeros(count)
    multiplier[0] = 1.0
    if count % 2 == 0:
        multiplier[count // 2] = 1.0
        multiplier[1:count // 2] = 2.0
    else:
        multiplier[1:(count + 1) // 2] = 2.0
    return np.fft.ifft(np.fft.fft(values, axis=-1) * multiplier, axis=-1)


def fourier_resample(values: np.ndarray, factor: int) -> np.ndarray:
    """实值周期信号的带限插值，保持原波形并提高时延采样密度。"""
    if factor == 1:
        return values.copy()
    count = values.shape[-1]
    target_count = count * factor
    spectrum = np.fft.fft(values, axis=-1)
    padded = np.zeros((values.shape[0], target_count), dtype=complex)
    padded[:, :count // 2] = spectrum[:, :count // 2]
    padded[:, count // 2] = spectrum[:, count // 2] / 2
    padded[:, target_count - count // 2] = spectrum[:, count // 2] / 2
    padded[:, target_count - count // 2 + 1:] = spectrum[:, count // 2 + 1:]
    return np.fft.ifft(padded, axis=-1).real * factor


def shift_rows(values: np.ndarray, shifts) -> np.ndarray:
    """循环平移；正数表示延迟，支持每行使用不同平移量。"""
    values = np.asarray(values)
    frequency = np.fft.fftfreq(values.shape[-1])
    shifts = np.atleast_1d(shifts).astype(float)
    if shifts.size == 1:
        phase = np.exp(-2j * np.pi * frequency * shifts[0])[None, :]
    else:
        if shifts.size != values.shape[0]:
            raise ValueError("每行必须对应一个平移量")
        phase = np.exp(-2j * np.pi * frequency[None, :] * shifts[:, None])
    result = np.fft.ifft(np.fft.fft(values, axis=-1) * phase, axis=-1)
    return result.real if np.isrealobj(values) else result


def interpolated_maximum(curve: np.ndarray, index: int) -> float:
    left = curve[(index - 1) % curve.size]
    middle = curve[index]
    right = curve[(index + 1) % curve.size]
    denominator = left - 2 * middle + right
    delta = 0.0 if abs(denominator) < EPS else 0.5 * (left - right) / denominator
    return (index + np.clip(delta, -1.0, 1.0)) % curve.size


def calibrated_aligned_profile(group_dir: Path, rho_m: np.ndarray, correction: np.ndarray,
                               valid: np.ndarray) -> np.ndarray:
    measured = load_group(group_dir)
    calibrated = apply_calibration(measured, correction, valid)
    return aligned_profile(calibrated, rho_m)


def build_direct_templates(data_root: Path, correction: np.ndarray, rho_m: np.ndarray,
                           valid: np.ndarray, halfwidth: int):
    """空场只含直射波和背景；对齐后按组等权平均，并限制模板支撑区。"""
    profiles = []
    centers = []
    direct_mask = np.abs(circular_offset(0.0)) <= halfwidth
    groups = discover_groups(data_root, "空场数据")
    for _, group_dir in groups:
        profile = calibrated_aligned_profile(group_dir, rho_m, correction, valid)
        center = consensus_center(profile, valid)
        aligned = shift_rows(profile, -center)
        channel_rms = np.sqrt(np.mean(aligned[valid][:, direct_mask] ** 2, axis=1))
        group_scale = np.median(channel_rms) + EPS
        profiles.append(aligned / group_scale)
        centers.append(center)
    templates = np.mean(profiles, axis=0) * hann_gate(0.0, halfwidth)[None, :]
    return templates, np.asarray(centers), [path for _, path in groups]


def locate_direct(profile: np.ndarray, templates: np.ndarray, valid: np.ndarray):
    """在最强相关峰之前寻找最早显著峰簇，避免强金属反射冒充直射波。"""
    spectrum = np.fft.fft(profile, axis=1)
    template_spectrum = np.fft.fft(templates, axis=1)
    correlation = np.fft.ifft(spectrum * np.conj(template_spectrum), axis=1).real
    normalization = np.sqrt(
        np.mean(profile ** 2, axis=1) * np.sum(templates ** 2, axis=1)
    ) + EPS
    normalized = np.abs(correlation[valid]) / normalization[valid, None]
    score = np.median(normalized, axis=0)
    strongest = int(np.argmax(score))
    offsets = np.arange(-45, 1)
    indices = (strongest + offsets) % score.size
    values = score[indices]
    active = values >= 0.20 * score[strongest]
    padded = np.r_[False, active, False].astype(int)
    changes = np.diff(padded)
    starts = np.flatnonzero(changes == 1)
    ends = np.flatnonzero(changes == -1)
    for start, end in zip(starts, ends):
        segment = values[start:end]
        if segment.size >= 3 and np.max(segment) >= 0.30 * score[strongest]:
            peak = int(indices[start + int(np.argmax(segment))])
            return interpolated_maximum(score, peak), score
    return interpolated_maximum(score, strongest), score


def stabilize_direct_centers(centers: np.ndarray) -> np.ndarray:
    """同一段采集的起点应稳定；仅利用多组一致性修复个别双峰误判。"""
    unwrapped = np.asarray(centers, dtype=float).copy()
    for index in range(1, unwrapped.size):
        difference = (unwrapped[index] - unwrapped[index - 1] + NP / 2) % NP - NP / 2
        unwrapped[index] = unwrapped[index - 1] + difference
    boundaries = np.r_[0, np.flatnonzero(np.abs(np.diff(unwrapped)) > 20) + 1, unwrapped.size]
    for start, end in zip(boundaries[:-1], boundaries[1:]):
        segment = unwrapped[start:end]
        center = np.median(segment)
        inliers = np.abs(segment - center) < 0.5
        if np.sum(inliers) < 3:
            continue
        for local_index in np.flatnonzero(~inliers):
            deviation = abs(segment[local_index] - center)
            if 0.75 < deviation < 6:
                unwrapped[start + local_index] = center
    return unwrapped % NP


def make_template_bank(templates: np.ndarray, valid: np.ndarray, delay_grid: np.ndarray):
    bank = np.empty((delay_grid.size, int(valid.sum()), NP), dtype=float)
    for index, delay in enumerate(delay_grid):
        bank[index] = shift_rows(templates[valid], delay)
    return bank


def suppress_direct(profile: np.ndarray, templates: np.ndarray, valid: np.ndarray,
                    template_bank: np.ndarray, delay_grid: np.ndarray,
                    direct_halfwidth: int, fit_halfwidth: int):
    """仅用直射核心窗拟合幅度和分数时延，再减去完整直射模板。"""
    fit_mask = np.abs(circular_offset(0.0)) <= fit_halfwidth
    direct_mask = np.abs(circular_offset(0.0)) <= direct_halfwidth
    measured = profile[valid][:, fit_mask]
    bank_fit = template_bank[:, :, fit_mask]
    denominator = np.sum(bank_fit ** 2, axis=2) + EPS
    amplitude = np.sum(measured[None, :, :] * bank_fit, axis=2) / denominator
    error = np.mean(
        (measured[None, :, :] - amplitude[:, :, None] * bank_fit) ** 2,
        axis=2,
    )
    best = np.argmin(error, axis=0)
    channel = np.arange(int(valid.sum()))
    selected_amplitude = amplitude[best, channel]
    selected_template = template_bank[best, channel]
    residual = np.zeros_like(profile)
    residual[valid] = profile[valid] - selected_amplitude[:, None] * selected_template

    before_energy = np.sum(profile[valid][:, direct_mask] ** 2)
    after_energy = np.sum(residual[valid][:, direct_mask] ** 2)
    suppression_db = 10 * np.log10((before_energy + EPS) / (after_energy + EPS))
    direct_scale = np.sqrt(np.sum(profile[valid][:, direct_mask] ** 2, axis=1)) + EPS
    details = {
        "amplitude": selected_amplitude,
        "fractional_delay": delay_grid[best],
        "direct_scale": direct_scale,
        "suppression_db": float(suppression_db),
    }
    return residual, details


def sample_rows(values: np.ndarray, positions: np.ndarray) -> np.ndarray:
    """对每行在各自的非整数循环采样位置上线性插值。"""
    positions = np.asarray(positions, dtype=float)
    base = np.floor(positions).astype(int)
    fraction = positions - base
    left = base % values.shape[1]
    right = (base + 1) % values.shape[1]
    rows = np.arange(values.shape[0])[:, None]
    return values[rows, left] * (1 - fraction) + values[rows, right] * fraction


def target_delays(distance_m: float, rho_valid: np.ndarray) -> np.ndarray:
    path = np.sqrt(rho_valid ** 2 + 4 * distance_m ** 2)
    return (path - rho_valid) * FS / C


def focus_curve(residual: np.ndarray, direct_scale: np.ndarray, quality: np.ndarray,
                rho_valid: np.ndarray, distances: np.ndarray, stack_halfwidth: int,
                upsample_factor: int):
    """同时计算相干与非相干聚焦曲线，方法选择只使用校准组。"""
    interpolated = fourier_resample(residual, upsample_factor)
    analytic = analytic_signal(interpolated)
    base_weight = np.maximum(quality, EPS) / direct_scale
    base_weight /= np.sum(base_weight)
    offsets = np.arange(-stack_halfwidth, stack_halfwidth + 1)
    coherent = np.empty(distances.size)
    incoherent = np.empty(distances.size)
    for index, distance in enumerate(distances):
        path = np.sqrt(rho_valid ** 2 + 4 * distance ** 2)
        delays = (path - rho_valid) * FS * upsample_factor / C
        positions = delays[:, None] + offsets[None, :] * upsample_factor
        samples = sample_rows(analytic, positions)
        weight = base_weight * path / rho_valid
        weight /= np.sum(weight)
        stacked = np.sum(weight[:, None] * samples, axis=0)
        coherent[index] = np.sum(np.abs(stacked) ** 2)
        incoherent[index] = np.sum(weight[:, None] * np.abs(samples) ** 2)
    return coherent, incoherent, analytic


def grid_peak(distances: np.ndarray, score: np.ndarray) -> float:
    index = int(np.argmax(score))
    if index == 0 or index == distances.size - 1:
        return float(distances[index])
    left, middle, right = score[index - 1:index + 2]
    denominator = left - 2 * middle + right
    delta = 0.0 if abs(denominator) < EPS else 0.5 * (left - right) / denominator
    return float(distances[index] + np.clip(delta, -1, 1) * (distances[1] - distances[0]))


def differential_distance(analytic: np.ndarray, focus_distance: float,
                          rho_valid: np.ndarray, upsample_factor: int) -> float:
    """在聚焦结果附近精化各通道目标峰，再用直射—目标差分时延测距。"""
    expected = target_delays(focus_distance, rho_valid) * upsample_factor
    offsets = np.linspace(-3.0, 3.0, 25) * upsample_factor
    positions = expected[:, None] + offsets[None, :]
    magnitude = np.abs(sample_rows(analytic, positions))
    peak_position = positions[np.arange(rho_valid.size), np.argmax(magnitude, axis=1)]
    path = rho_valid + C * peak_position / (FS * upsample_factor)
    distances = 0.5 * np.sqrt(np.maximum(path ** 2 - rho_valid ** 2, 0.0))
    return float(np.median(distances))


def target_preservation(profile: np.ndarray, residual: np.ndarray,
                        true_distance: float, rho_valid: np.ndarray) -> float:
    delays = target_delays(true_distance, rho_valid)
    offsets = np.arange(-2, 3)
    positions = delays[:, None] + offsets[None, :]
    before = np.sum(sample_rows(profile, positions) ** 2)
    after = np.sum(sample_rows(residual, positions) ** 2)
    return float(10 * np.log10((after + EPS) / (before + EPS)))


def process_group(group_dir: Path, kind: str, group_index: int, true_distance: float,
                  correction: np.ndarray, quality: np.ndarray, rho_m: np.ndarray,
                  valid: np.ndarray, templates: np.ndarray, template_bank: np.ndarray,
                  delay_grid: np.ndarray, distances: np.ndarray, args,
                  original: np.ndarray | None = None, center: float | None = None):
    if original is None:
        original = calibrated_aligned_profile(group_dir, rho_m, correction, valid)
    if center is None:
        center, _ = locate_direct(original, templates, valid)
    profile = shift_rows(original, -center)
    residual, details = suppress_direct(
        profile, templates, valid, template_bank, delay_grid,
        args.direct_halfwidth, args.fit_halfwidth,
    )
    rho_valid = rho_m[valid]
    coherent, incoherent, analytic = focus_curve(
        residual[valid], details["direct_scale"], quality,
        rho_valid, distances, args.stack_halfwidth, args.upsample_factor,
    )
    coherent_distance = grid_peak(distances, coherent)
    incoherent_distance = grid_peak(distances, incoherent)
    preservation = target_preservation(
        profile[valid], residual[valid], true_distance, rho_valid,
    )
    row = {
        "kind": kind,
        "group_index": group_index,
        "group": group_dir.name,
        "split": "calibration" if group_index <= 10 else "test",
        "true_distance_m": true_distance,
        "direct_center_sample": center,
        "direct_suppression_db": details["suppression_db"],
        "target_preservation_db": preservation,
        "coherent_distance_m": coherent_distance,
        "coherent_error_cm": 100 * (coherent_distance - true_distance),
        "incoherent_distance_m": incoherent_distance,
        "incoherent_error_cm": 100 * (incoherent_distance - true_distance),
        "coherent_differential_m": differential_distance(
            analytic, coherent_distance, rho_valid, args.upsample_factor,
        ),
        "incoherent_differential_m": differential_distance(
            analytic, incoherent_distance, rho_valid, args.upsample_factor,
        ),
    }
    example = {
        "profile": profile[valid].copy(),
        "residual": residual[valid].copy(),
        "rho": rho_valid,
        "coherent": coherent,
        "incoherent": incoherent,
        "distances": distances,
        "true_distance": true_distance,
        "coherent_distance": coherent_distance,
        "incoherent_distance": incoherent_distance,
    }
    return row, example


def error_metrics(rows, method: str, bias_m: float = 0.0):
    errors = np.array([
        100 * (row[f"{method}_distance_m"] - bias_m - row["true_distance_m"])
        for row in rows
    ])
    return {
        "count": len(rows),
        "mae_cm": float(np.mean(np.abs(errors))),
        "rmse_cm": float(np.sqrt(np.mean(errors ** 2))),
        "max_absolute_error_cm": float(np.max(np.abs(errors))),
        "bias_cm": float(np.mean(errors)),
    }


def save_figures(rows, examples, selected_methods, selected_biases, output_dir: Path,
                 reference: int, valid: np.ndarray):
    valid_indices = np.flatnonzero(valid)
    reference_row = int(np.argmin(np.abs(valid_indices - reference)))
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    for line, kind in enumerate(("wall", "metal")):
        example = examples[kind]
        rho = example["rho"]
        expected = target_delays(example["true_distance"], rho)
        axis = np.arange(-8, 46)
        positions = np.full((rho.size, axis.size), axis[None, :])
        before = sample_rows(example["profile"], positions)[reference_row]
        after = sample_rows(example["residual"], positions)[reference_row]
        scale = np.max(np.abs(before)) + EPS
        axes[line, 0].plot(axis, before / scale, label="Before suppression")
        axes[line, 0].plot(axis, after / scale, label="After suppression")
        axes[line, 0].axvline(expected[reference_row], color="black", linestyle="--", label="Known target")
        axes[line, 0].set_title(f"{kind}: direct-aligned range profile")
        axes[line, 0].set_xlabel("Delay relative to direct wave / samples")
        axes[line, 0].set_ylabel("Normalized amplitude")
        axes[line, 0].legend(fontsize=8)

        method = selected_methods[kind]
        score = example[method]
        score = score / (np.max(score) + EPS)
        axes[line, 1].plot(example["distances"], score, label=f"{method} focus")
        axes[line, 1].axvline(example["true_distance"], color="black", linestyle="--", label="Known")
        corrected_estimate = example[f"{method}_distance"] - selected_biases[kind]
        axes[line, 1].axvline(corrected_estimate, color="tab:red", linestyle=":", label="Estimated")
        axes[line, 1].set_title(f"{kind}: selected {method} focus")
        axes[line, 1].set_xlabel("Candidate distance / m")
        axes[line, 1].set_ylabel("Normalized score")
        axes[line, 1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(output_dir / "suppression_and_focus_examples.png", dpi=170)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    markers = {"wall": "o", "metal": "s"}
    for kind in ("wall", "metal"):
        for split in ("calibration", "test"):
            selected = [row for row in rows if row["kind"] == kind and row["split"] == split]
            true = np.array([row["true_distance_m"] for row in selected])
            estimate = np.array([row["selected_distance_m"] for row in selected])
            axes[0].scatter(true, estimate, marker=markers[kind],
                            facecolors="none" if split == "test" else None,
                            label=f"{kind} {split}")
            axes[1].scatter([row["group"] for row in selected],
                            np.abs(100 * (estimate - true)),
                            marker=markers[kind], label=f"{kind} {split}")
    limits = [0.35, 1.3]
    axes[0].plot(limits, limits, "k--", linewidth=1)
    axes[0].set_xlim(limits)
    axes[0].set_ylim(limits)
    axes[0].set_aspect("equal")
    axes[0].set_xlabel("Known distance / m")
    axes[0].set_ylabel("Estimated distance / m")
    axes[0].set_title("Ranging estimates")
    axes[0].legend(fontsize=8)
    axes[1].set_ylabel("Absolute error / cm")
    axes[1].set_title("Absolute error by group")
    axes[1].tick_params(axis="x", rotation=90, labelsize=7)
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(output_dir / "ranging_results.png", dpi=170)
    plt.close(fig)


def parse_arguments():
    parser = argparse.ArgumentParser(description="问题1.2直射波抑制与问题1.3多通道测距")
    parser.add_argument("--data-root", type=Path, default=ROOT)
    parser.add_argument("--calibration", type=Path, default=CALIBRATION)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).with_name("ranging_output"))
    parser.add_argument("--direct-halfwidth", type=int, default=5)
    parser.add_argument("--fit-halfwidth", type=int, default=3)
    parser.add_argument("--max-fit-delay", type=float, default=0.8, help="单位：采样点")
    parser.add_argument("--fit-delay-step", type=float, default=0.05, help="单位：采样点")
    parser.add_argument("--range-min", type=float, default=0.30)
    parser.add_argument("--range-max", type=float, default=1.40)
    parser.add_argument("--range-step", type=float, default=0.001)
    parser.add_argument("--stack-halfwidth", type=int, default=2)
    parser.add_argument("--upsample-factor", type=int, default=4)
    return parser.parse_args()


def main():
    args = parse_arguments()
    if not args.calibration.exists():
        raise FileNotFoundError(f"请先运行 channel_calibration.py：{args.calibration}")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    *_, rho_m, valid, _ = geometry()
    calibration = np.load(args.calibration)
    correction = calibration["complex_correction"]
    quality = calibration["quality_score"]
    reference = int(calibration["reference_index_0based"])

    templates, empty_centers, _ = build_direct_templates(
        args.data_root, correction, rho_m, valid, args.direct_halfwidth,
    )
    delay_grid = np.arange(
        -args.max_fit_delay, args.max_fit_delay + args.fit_delay_step / 2,
        args.fit_delay_step,
    )
    template_bank = make_template_bank(templates, valid, delay_grid)
    distances = np.arange(args.range_min, args.range_max + args.range_step / 2, args.range_step)

    rows = []
    examples = {}
    for kind, folder in (("wall", "墙体数据"), ("metal", "金属板数据")):
        prepared = []
        print(f"Locating direct waves for {kind}", flush=True)
        for group_index, group_dir in discover_groups(args.data_root, folder):
            match = re.search(r"-(\d+)cm", group_dir.name)
            if not match:
                raise ValueError(f"缺少距离标签：{group_dir.name}")
            true_distance = int(match.group(1)) / 100
            original = calibrated_aligned_profile(group_dir, rho_m, correction, valid)
            center, _ = locate_direct(original, templates, valid)
            prepared.append((group_index, group_dir, true_distance, original, center))
        stabilized = stabilize_direct_centers(np.array([item[4] for item in prepared]))
        for (group_index, group_dir, true_distance, original, _), center in zip(prepared, stabilized):
            print(f"Processing {kind} data{group_index}: {true_distance:.2f} m", flush=True)
            row, example = process_group(
                group_dir, kind, group_index, true_distance,
                correction, quality, rho_m, valid, templates, template_bank,
                delay_grid, distances, args, original=original, center=center,
            )
            rows.append(row)
            if group_index == 10:
                examples[kind] = example

    selected_methods = {}
    selected_biases = {}
    selection_metrics = {}
    for kind in ("wall", "metal"):
        training = [row for row in rows if row["kind"] == kind and row["split"] == "calibration"]
        metrics = {}
        biases = {}
        for method in ("coherent", "incoherent"):
            bias = float(np.mean([
                row[f"{method}_distance_m"] - row["true_distance_m"] for row in training
            ]))
            biases[method] = bias
            metrics[method] = error_metrics(training, method, bias)
            metrics[method]["estimated_range_bias_cm"] = 100 * bias
        selected_methods[kind] = min(metrics, key=lambda method: metrics[method]["rmse_cm"])
        selected_biases[kind] = biases[selected_methods[kind]]
        selection_metrics[kind] = metrics

    for row in rows:
        method = selected_methods[row["kind"]]
        bias = selected_biases[row["kind"]]
        row["selected_method"] = method
        row["uncorrected_selected_distance_m"] = row[f"{method}_distance_m"]
        row["range_bias_m"] = bias
        row["selected_distance_m"] = row[f"{method}_distance_m"] - bias
        row["selected_error_cm"] = 100 * (row["selected_distance_m"] - row["true_distance_m"])
        row["differential_distance_m"] = row[f"{method}_differential_m"]

    fieldnames = list(rows[0])
    with (args.output_dir / "ranging_results.csv").open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    evaluation = {}
    for kind in ("wall", "metal"):
        evaluation[kind] = {
            "selected_method": selected_methods[kind],
            "range_bias_cm": 100 * selected_biases[kind],
        }
        for split in ("calibration", "test"):
            selected = [row for row in rows if row["kind"] == kind and row["split"] == split]
            evaluation[kind][split] = error_metrics(selected, "selected")
            evaluation[kind][split]["mean_direct_suppression_db"] = float(
                np.mean([row["direct_suppression_db"] for row in selected])
            )
            evaluation[kind][split]["mean_target_preservation_db"] = float(
                np.mean([row["target_preservation_db"] for row in selected])
            )
    summary = {
        "reference_channel": reference,
        "direct_halfwidth_samples": args.direct_halfwidth,
        "fit_halfwidth_samples": args.fit_halfwidth,
        "range_grid_m": [args.range_min, args.range_max, args.range_step],
        "upsample_factor": args.upsample_factor,
        "selection_on_calibration_groups": selection_metrics,
        "evaluation": evaluation,
    }
    with (args.output_dir / "ranging_summary.json").open("w", encoding="utf-8") as file:
        json.dump(summary, file, ensure_ascii=False, indent=2)
    np.savez_compressed(
        args.output_dir / "direct_templates.npz",
        templates=templates[valid], valid_channel_index=np.flatnonzero(valid),
        rho_m=rho_m[valid], empty_direct_centers=empty_centers,
        fit_delay_grid=delay_grid,
    )
    save_figures(rows, examples, selected_methods, selected_biases,
                 args.output_dir, reference, valid)

    print("\nSelected methods:", selected_methods)
    for kind in ("wall", "metal"):
        for split in ("calibration", "test"):
            print(kind, split, evaluation[kind][split])
    print("\nPer-group selected estimates:")
    for row in rows:
        print(f"{row['kind']:5s} data{row['group_index']:02d} {row['split']:11s} "
              f"true={row['true_distance_m']:.3f} m estimated={row['selected_distance_m']:.3f} m "
              f"error={row['selected_error_cm']:+.2f} cm suppression={row['direct_suppression_db']:.2f} dB")


if __name__ == "__main__":
    main()
