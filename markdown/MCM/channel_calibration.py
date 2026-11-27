# -*- coding: utf-8 -*-
"""单发多收雷达通道校准。

约定：H_i(f)=Y_i(f)/Y_ref(f) 已完成几何传播补偿；
H_i 的线性相位为 -2*pi*f*delay_i，delay_i>0 表示该通道相对参考通道滞后。
校准时将校正频响 1/H_i(f) 应用于第 i 通道。
"""
import argparse
import csv
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

FS = 4e9
NP = 4000
F_START = 0.3e9
F_STOP = 1.7e9
C0 = 299792458.0
TX_INDEX = 3 * 8 + 3
DEFAULT_ROOT = Path(r"C:\Users\wangq\Desktop\2027年电子科大美赛模拟赛竞赛题目\竞赛题目\A 题：单发多收下的雷达信号处理及成像问题\附件\附件2-测距数据")

N = np.arange(NP)
T = N / FS
TX = 30000 * (0.54 - 0.46 * np.cos(2 * np.pi * N / (NP - 1))) * np.cos(
    2 * np.pi * (F_START * T + 0.5 * (F_STOP - F_START) / (NP / FS) * T**2)
)
TX_F = np.fft.fft(TX)
FFREQ = np.fft.fftfreq(NP, 1 / FS)
BAND = np.flatnonzero((FFREQ >= F_START) & (FFREQ <= F_STOP))
FREQ = FFREQ[BAND]
F_CENTER = 1e9


def geometry():
    rows = np.repeat(np.arange(8), 8)
    slots = np.tile(np.arange(8), 8)
    cols = 2 * slots + rows % 2  # 从 0 开始的实际阵列列号
    x_cm = cols * 3.5
    z_cm = 75.5 - 7 * rows
    tx_x, tx_z = x_cm[TX_INDEX], z_cm[TX_INDEX]
    rho_m = np.hypot(x_cm - tx_x, z_cm - tx_z) / 100
    valid = np.arange(64) != TX_INDEX
    labels = np.array([
        f"R{rows[i]+1}-A{slots[i]+1}-C{cols[i]+1}" for i in range(64)
    ])
    return rows, slots, cols, x_cm, z_cm, rho_m, valid, labels


def read_dat_period(path):
    """读取一个数据包文件；按采样时刻解交织，并周期平均为 8×4000。"""
    buf = Path(path).read_bytes()
    pos = 0
    packets = []
    while pos + 28 <= len(buf):
        magic = int(np.frombuffer(buf, "<u4", 1, pos)[0])
        if magic != 963072:
            pos += 4
            continue
        total_len, ptype = np.frombuffer(buf, "<u4", 2, pos + 4)
        pos += 12
        if ptype != 102:
            pos += int(total_len) - 8
            continue
        header = np.frombuffer(buf, "<u4", 4, pos)
        num, ln = int(header[2]), int(header[3])
        pos += 16
        count = num * ln // 2
        if pos + 2 * count > len(buf):
            break
        raw = np.frombuffer(buf, "<i2", count, pos).astype(np.float64)
        pos += 2 * count
        # MATLAB reshape(8,[]) 的等价写法；不能直接 reshape(8,-1)。
        packets.append(raw.reshape(-1, 8).T)
    if not packets:
        raise ValueError(f"未找到采样包: {path}")
    samples = np.stack(packets)
    if samples.shape[-1] % NP:
        raise ValueError(f"采样点数不是 {NP} 的整数倍: {path}")
    periods = samples.reshape(len(packets), 8, -1, NP)
    return periods.mean(axis=(0, 2))


def load_group(group_dir):
    row_data = []
    for row in range(8):
        files = list(Path(group_dir).glob(f"*_{row}.dat"))
        if len(files) != 1:
            raise FileNotFoundError(f"{group_dir} 中第 {row + 1} 行文件数量为 {len(files)}")
        row_data.append(read_dat_period(files[0]))
    return np.concatenate(row_data, axis=0)


def circular_offset(center=0.0):
    return (np.arange(NP) - center + NP / 2) % NP - NP / 2


def interpolated_peak(curve, index):
    index = int(index) % NP
    left, middle, right = (abs(curve[(index + k) % NP]) for k in (-1, 0, 1))
    denominator = left - 2 * middle + right
    delta = 0.0 if abs(denominator) < 1e-12 else 0.5 * (left - right) / denominator
    return (index + np.clip(delta, -0.5, 0.5)) % NP


def consensus_center(profile, valid, expected=None, search_half=None):
    scale = np.sqrt(np.mean(profile[valid] ** 2, axis=1)) + 1e-12
    score = np.median(np.abs(profile[valid]) / scale[:, None], axis=0)
    if expected is None:
        index = int(np.argmax(score))
    else:
        offsets = np.arange(-int(search_half), int(search_half) + 1)
        indices = (int(round(expected)) + offsets) % NP
        index = indices[int(np.argmax(score[indices]))]
    return interpolated_peak(score, index)


def aligned_profile(y, path_m):
    matched = np.fft.fft(y - y.mean(axis=1, keepdims=True), axis=1) * np.conj(TX_F)
    geometry_phase = np.exp(2j * np.pi * FFREQ[None, :] * (path_m[:, None] / C0))
    return np.fft.ifft(matched * geometry_phase, axis=1).real


def hann_gate(center, halfwidth):
    offsets = circular_offset(center)
    gate = np.zeros(NP)
    inside = np.abs(offsets) < halfwidth
    gate[inside] = 0.5 + 0.5 * np.cos(np.pi * offsets[inside] / halfwidth)
    return gate


def direct_observation(y, rho_m, valid, halfwidth, keep_profile=False):
    profile = aligned_profile(y, rho_m)
    center = consensus_center(profile, valid)
    gate = hann_gate(center, halfwidth)
    spectra = np.fft.fft(profile * gate, axis=1) * rho_m[:, None]
    offsets = circular_offset(center)
    noise = np.abs(offsets) > max(12, 2 * halfwidth)
    quality = np.zeros(64)
    for i in np.flatnonzero(valid):
        local = np.abs(offsets) <= max(5, halfwidth)
        peak = np.max(np.abs(profile[i, local]))
        quality[i] = peak / (np.sqrt(np.mean(profile[i, noise] ** 2)) + 1e-12)
    result = {"kind": "empty", "C": spectra, "center": center}
    if keep_profile:
        result.update(profile=profile, path_m=rho_m)
    return result, quality


def response_from_observations(observations, reference):
    cross = np.zeros((64, NP), dtype=complex)
    power = np.zeros((64, NP))
    reference_power = np.zeros(NP)
    for observation in observations:
        spectra = observation["C"]
        scale = np.sqrt(np.mean(np.abs(spectra[reference, BAND]) ** 2)) + 1e-12
        spectra = spectra / scale  # 每次测量等权，同时保留通道间幅度比
        cross += spectra * np.conj(spectra[reference])
        power += np.abs(spectra) ** 2
        reference_power += np.abs(spectra[reference]) ** 2
    regularizer = 1e-8 * np.max(reference_power)
    response = cross / (reference_power[None, :] + regularizer)
    coherence = np.abs(cross) ** 2 / (power * reference_power[None, :] + regularizer)
    return response, np.clip(coherence.real, 0, 1)


def smooth(values, width=31):
    kernel = np.hamming(width)
    kernel /= kernel.sum()
    pad = width // 2
    return np.convolve(np.pad(values, pad, mode="reflect"), kernel, mode="valid")


def fit_delay(response, coherence, valid):
    delays = np.full(64, np.nan)
    fits = {}
    x = FREQ - F_CENTER
    for i in np.flatnonzero(valid):
        h = response[i] if response.shape[1] == len(BAND) else response[i, BAND]
        c = coherence[i] if coherence.shape[1] == len(BAND) else coherence[i, BAND]
        phase = np.unwrap(np.angle(h))
        base_weight = np.maximum(c, 1e-4) ** 2
        weight = base_weight.copy()
        for _ in range(3):
            matrix = np.column_stack((x, np.ones_like(x)))
            normal = matrix.T @ (weight[:, None] * matrix)
            rhs = matrix.T @ (weight * phase)
            slope, intercept = np.linalg.solve(normal + np.eye(2) * 1e-12, rhs)
            residual = phase - slope * x - intercept
            scale = 1.4826 * np.median(np.abs(residual - np.median(residual))) + 1e-6
            weight = base_weight / (1 + (residual / (3 * scale)) ** 2)
        delays[i] = -slope / (2 * np.pi)
        fits[i] = slope
    return delays, fits


def decompose_response(response, coherence, reference, valid):
    delay_s, slopes = fit_delay(response, coherence, valid)
    model = np.ones((64, len(BAND)), dtype=complex)
    correction = np.ones_like(model)
    gain = np.ones((64, len(BAND)))
    residual_phase = np.zeros((64, len(BAND)))
    x = FREQ - F_CENTER
    for i in np.flatnonzero(valid):
        if i == reference:
            delay_s[i] = 0.0
            continue
        h = response[i, BAND]
        slope = slopes[i]
        delay_removed = h * np.exp(-1j * slope * x)
        gain[i] = np.maximum(smooth(np.abs(h)), 1e-3)
        residual_phase[i] = smooth(np.unwrap(np.angle(delay_removed)))
        model[i] = gain[i] * np.exp(1j * (slope * x + residual_phase[i]))
        correction[i] = 1 / model[i]
    return delay_s, model, correction, gain, residual_phase


def circular_phase_rms(response, valid, exclude):
    indices = [i for i in np.flatnonzero(valid) if i != exclude]
    values = []
    for i in indices:
        phase = np.angle(response[i])
        values.append(np.sqrt(np.mean(phase**2)))
    return float(np.median(values))


def gain_rms(response, valid, exclude):
    indices = [i for i in np.flatnonzero(valid) if i != exclude]
    values = []
    for i in indices:
        gain_db = 20 * np.log10(np.maximum(np.abs(response[i]), 1e-9))
        values.append(np.sqrt(np.mean(gain_db**2)))
    return float(np.median(values))


def validation_metrics(observations, reference, valid, model):
    response, coherence = response_from_observations(observations, reference)
    measured = response[:, BAND]
    corrected = measured / model
    before_delay, _ = fit_delay(response, coherence, valid)
    after_delay, _ = fit_delay(corrected, coherence, valid)
    indices = [i for i in np.flatnonzero(valid) if i != reference]
    return {
        "phase_before_deg": np.degrees(circular_phase_rms(measured, valid, reference)),
        "phase_after_deg": np.degrees(circular_phase_rms(corrected, valid, reference)),
        "gain_before_db": gain_rms(measured, valid, reference),
        "gain_after_db": gain_rms(corrected, valid, reference),
        "delay_std_before_ns": float(np.nanstd(before_delay[indices]) * 1e9),
        "delay_std_after_ns": float(np.nanstd(after_delay[indices]) * 1e9),
    }, response


def full_correction(correction_row):
    full = np.ones(NP, dtype=complex)
    full[BAND] = correction_row
    full[(-BAND) % NP] = np.conj(correction_row)
    return full


def apply_calibration(y, correction, valid):
    """将 NPZ 中的 63×1400 校正频响应用于 63 或 64 通道周期数据。"""
    result = np.fft.fft(y, axis=1)
    for row, channel in enumerate(np.flatnonzero(valid)):
        result[channel] *= full_correction(correction[row])
    return np.fft.ifft(result, axis=1).real


def make_figure(output, delay_s, valid, labels, reference, representative,
                validation_response, model, observation):
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))

    indices = np.flatnonzero(valid)
    colors = ["#c44e52" if i == reference else "#4c72b0" for i in indices]
    axes[0, 0].bar(np.arange(len(indices)), delay_s[indices] * 1e9, color=colors)
    axes[0, 0].axhline(0, color="black", linewidth=0.8)
    axes[0, 0].set_title("各通道相对时延（红色为参考通道）")
    axes[0, 0].set_xlabel("接收通道序号（已跳过发射通道）")
    axes[0, 0].set_ylabel("滞后量 / ns")
    axes[0, 0].grid(alpha=0.25)

    before = validation_response[representative, BAND]
    after = before / model[representative]
    axes[0, 1].plot(FREQ / 1e9, 20 * np.log10(np.maximum(np.abs(before), 1e-9)), label="校准前")
    axes[0, 1].plot(FREQ / 1e9, 20 * np.log10(np.maximum(np.abs(after), 1e-9)), label="校准后")
    axes[0, 1].axhline(0, color="black", linewidth=0.8)
    axes[0, 1].set_title(f"{labels[representative]} 相对参考通道的幅度频响")
    axes[0, 1].set_xlabel("数字频率 / GHz")
    axes[0, 1].set_ylabel("幅度 / dB")
    axes[0, 1].legend()
    axes[0, 1].grid(alpha=0.25)

    axes[1, 0].plot(FREQ / 1e9, np.degrees(np.unwrap(np.angle(before))), label="校准前")
    axes[1, 0].plot(FREQ / 1e9, np.degrees(np.unwrap(np.angle(after))), label="校准后")
    axes[1, 0].axhline(0, color="black", linewidth=0.8)
    axes[1, 0].set_title("相对参考通道的相位频响")
    axes[1, 0].set_xlabel("数字频率 / GHz")
    axes[1, 0].set_ylabel("相位 / °")
    axes[1, 0].legend()
    axes[1, 0].grid(alpha=0.25)

    profile = observation["profile"]
    path_m = observation["path_m"]
    corrected = apply_calibration(profile, 1 / model[valid], valid)
    corrected_profile = corrected[representative]
    offsets = np.arange(-12, 13)
    sample_indices = (int(round(observation["center"])) + offsets) % NP
    reference_curve = profile[reference, sample_indices] * path_m[reference]
    before_curve = profile[representative, sample_indices] * path_m[representative]
    after_curve = corrected_profile[sample_indices] * path_m[representative]
    for curve, name, style in (
        (reference_curve, "参考通道", "k-"),
        (before_curve, "代表通道校准前", "C0--"),
        (after_curve, "代表通道校准后", "C1-"),
    ):
        normalized = curve / (np.max(np.abs(curve)) + 1e-12)
        axes[1, 1].plot(offsets / FS * 1e9, normalized, style, label=name)
    axes[1, 1].set_title("几何对齐后的直达波脉冲压缩波形（分别归一化）")
    axes[1, 1].set_xlabel("相对直达波窗中心 / ns")
    axes[1, 1].set_ylabel("归一化幅度")
    axes[1, 1].legend()
    axes[1, 1].grid(alpha=0.25)

    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)


def discover_groups(root, folder):
    groups = []
    for path in (root / folder).iterdir():
        match = re.fullmatch(r"data(\d+)(?:-(\d+)cm)?", path.name)
        if path.is_dir() and match:
            groups.append((int(match.group(1)), path, match.group(2)))
    return [(item[0], item[1]) for item in sorted(groups)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).parent / "calibration_output")
    parser.add_argument("--gate-halfwidth", type=float, default=8.0, help="脉冲压缩域汉宁窗半宽，单位：采样点")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    rows, slots, cols, x_cm, z_cm, rho_m, valid, labels = geometry()
    direct_observations = []
    qualities = []
    groups = discover_groups(args.data_root, "空场数据")
    split = len(groups) // 2
    first_validation = None
    for group_number, (_, path) in enumerate(groups):
        y = load_group(path)
        keep_profile = group_number == split
        observation, quality = direct_observation(
            y, rho_m, valid, args.gate_halfwidth, keep_profile=keep_profile
        )
        direct_observations.append(observation)
        qualities.append(quality)
        if keep_profile:
            first_validation = observation
        print(f"空场 {path.name}: 直达波中心 {observation['center']:.2f} 点")

    calibration_observations = direct_observations[:split]
    validation_observations = direct_observations[split:]
    quality_score = np.median(np.stack(qualities[:split]), axis=0)
    candidates = np.flatnonzero(valid)
    reference = candidates[np.argmax(quality_score[candidates])]
    print(f"参考通道: {reference + 1} ({labels[reference]}), 质量评分 {quality_score[reference]:.2f}")

    response, coherence = response_from_observations(calibration_observations, reference)
    delay_s, model, correction, gain, residual_phase = decompose_response(
        response, coherence, reference, valid
    )
    metrics, validation_response = validation_metrics(
        validation_observations, reference, valid, model
    )
    print(
        f"留出空场检验: 相位RMS {metrics['phase_before_deg']:.2f}° -> {metrics['phase_after_deg']:.2f}°, "
        f"幅度RMS {metrics['gain_before_db']:.2f} -> {metrics['gain_after_db']:.2f} dB, "
        f"通道时延标准差 {metrics['delay_std_before_ns']:.3f} -> {metrics['delay_std_after_ns']:.3f} ns"
    )

    candidates = np.flatnonzero(valid & (np.arange(64) != reference))
    representative = candidates[np.nanargmax(np.abs(delay_s[candidates]))]

    np.savez_compressed(
        args.output_dir / "channel_calibration.npz",
        channel_index_0based=np.flatnonzero(valid),
        channel_labels=labels[valid], row=rows[valid] + 1, antenna_in_row=slots[valid] + 1,
        array_column=cols[valid] + 1, x_cm=x_cm[valid], z_cm=z_cm[valid],
        reference_index_0based=reference, reference_label=labels[reference],
        frequencies_hz=FREQ, relative_delay_s=delay_s[valid],
        complex_response=model[valid], complex_correction=correction[valid],
        gain=gain[valid], residual_phase_rad=residual_phase[valid],
        coherence=coherence[valid][:, BAND], quality_score=quality_score[valid],
    )

    with (args.output_dir / "channel_summary.csv").open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow([
            "channel_index_1based", "label", "row", "antenna_in_row", "array_column",
            "x_cm", "z_cm", "is_reference", "quality_score", "relative_delay_ns",
            "advance_to_align_ns", "median_gain_db", "residual_phase_at_1GHz_deg",
        ])
        midband = int(np.argmin(np.abs(FREQ - F_CENTER)))
        for i in np.flatnonzero(valid):
            writer.writerow([
                i + 1, labels[i], rows[i] + 1, slots[i] + 1, cols[i] + 1,
                x_cm[i], z_cm[i], int(i == reference), quality_score[i],
                delay_s[i] * 1e9, delay_s[i] * 1e9,
                np.median(20 * np.log10(gain[i])),
                np.degrees(residual_phase[i, midband]),
            ])

    with (args.output_dir / "validation_metrics.csv").open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow(["data_type", *metrics.keys()])
        writer.writerow(["held_out_empty", *metrics.values()])

    make_figure(
        args.output_dir / "calibration_before_after.png", delay_s, valid, labels,
        reference, representative, validation_response, model, first_validation,
    )
    print(f"结果已保存到: {args.output_dir}")


if __name__ == "__main__":
    main()
