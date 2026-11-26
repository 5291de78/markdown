from __future__ import annotations

import argparse
import json
import math
import re
import struct
import threading
import webbrowser
from dataclasses import dataclass
from functools import lru_cache
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import numpy as np

FS = 4e9
PERIOD_SAMPLES = 4000
MAX_DISPLAY_POINTS = 1600
DEFAULT_ROOT = Path(
    r"C:\Users\wangq\Desktop\2027年电子科大美赛模拟赛竞赛题目"
    r"\竞赛题目\A 题：单发多收下的雷达信号处理及成像问题\附件"
)
RECEIVER_MASK = np.ones((8, 8), dtype=bool)
RECEIVER_MASK[3, 3] = False
CHANNELS = [
    {
        "index": sum(1 for r in range(row) for k in range(8) if not (r == 3 and k == 3))
        + sum(1 for k in range(column) if not (row == 3 and k == 3)),
        "row": row + 1,
        "column": column + 1,
        "actualColumn": 2 * column + 1 + row % 2,
        "label": (
            f"第 {row + 1} 行 · 行内 {column + 1} · "
            f"实际列 {2 * column + 1 + row % 2}"
        ),
    }
    for row in range(8)
    for column in range(8)
    if not (row == 3 and column == 3)
]


class RadarError(Exception):
    pass


@dataclass(frozen=True)
class RadarGroup:
    id: str
    label: str
    files: tuple[Path, ...]


def natural_key(value: str):
    return [int(part) if part.isdigit() else part for part in re.split(r"(\d+)", value)]


def files_in_range_folder(folder: Path):
    files = []
    for row in range(8):
        matches = [
            path
            for path in folder.glob(f"*_{row}.dat")
            if path.is_file() and path.stat().st_size > 0
        ]
        if len(matches) != 1:
            return None
        files.append(matches[0])
    return tuple(files)


def scan_groups(root: Path):
    groups = []
    ranging_root = root / "附件2-测距数据"
    if ranging_root.is_dir():
        for category in sorted(ranging_root.iterdir(), key=lambda p: natural_key(p.name)):
            if not category.is_dir():
                continue
            for folder in sorted(category.iterdir(), key=lambda p: natural_key(p.name)):
                if not folder.is_dir():
                    continue
                files = files_in_range_folder(folder)
                if files is not None:
                    groups.append(
                        RadarGroup(
                            id=f"range/{category.name}/{folder.name}",
                            label=f"测距 / {category.name} / {folder.name}",
                            files=files,
                        )
                    )

    imaging_root = root / "附件3-成像数据"
    if imaging_root.is_dir():
        for scene in sorted(imaging_root.iterdir(), key=lambda p: natural_key(p.name)):
            if not scene.is_dir():
                continue
            by_timestamp = {}
            for path in scene.glob("*.dat"):
                match = re.match(r"(.+)_16000_([0-7])\.dat$", path.name)
                if match and path.stat().st_size > 0:
                    by_timestamp.setdefault(match.group(1), {})[int(match.group(2))] = path
            for timestamp in sorted(by_timestamp):
                row_files = by_timestamp[timestamp]
                if set(row_files) != set(range(8)):
                    continue
                groups.append(
                    RadarGroup(
                        id=f"image/{scene.name}/{timestamp}",
                        label=f"成像 / {scene.name} / {timestamp}",
                        files=tuple(row_files[row] for row in range(8)),
                    )
                )
    return groups


def read_dat(file_path: Path):
    raw = file_path.read_bytes()
    packets = []
    packet_counts = []
    pos = 0

    while pos + 28 <= len(raw):
        magic, total_len, packet_type = struct.unpack_from("<III", raw, pos)
        if magic != 963072:
            pos += 4
            continue
        if packet_type != 102:
            if total_len < 4:
                raise RadarError(f"无效数据包长度：{file_path.name}")
            pos += 8 + total_len
            continue

        _, count, num, length = struct.unpack_from("<fIII", raw, pos + 12)
        data_start = pos + 28
        data_bytes = num * length
        data_end = data_start + data_bytes
        if data_bytes <= 0 or data_bytes % 16 != 0:
            raise RadarError(f"无效采样区大小：{file_path.name}")
        if data_end > len(raw):
            break

        values = np.frombuffer(
            raw,
            dtype="<i2",
            count=data_bytes // 2,
            offset=data_start,
        )
        packet = values.reshape(-1, 8).T.astype(np.float64)
        packets.append(packet)
        packet_counts.append(count)
        pos = data_end

    if not packets:
        raise RadarError(f"没有找到有效采样包：{file_path.name}")
    return packets, packet_counts


@lru_cache(maxsize=2)
def load_group(group: RadarGroup):
    rows = []
    expected_counts = None
    sample_count = None

    for file_path in group.files:
        packets, counts = read_dat(file_path)
        if expected_counts is None:
            expected_counts = counts
        elif counts != expected_counts:
            raise RadarError(f"同一组各行的数据包编号不一致：{file_path.name}")
        if sample_count is None:
            sample_count = packets[0].shape[1]
        if any(packet.shape != (8, sample_count) for packet in packets):
            raise RadarError(f"数据包形状不一致：{file_path.name}")
        rows.append(np.stack(packets, axis=0))

    cube = np.stack(rows, axis=1)
    raw = cube[:, RECEIVER_MASK, :]
    return raw, np.asarray(expected_counts, dtype=np.int64)


def analytic_signal(signal):
    sample_count = signal.shape[-1]
    multiplier = np.zeros(sample_count)
    multiplier[0] = 1
    if sample_count % 2 == 0:
        multiplier[sample_count // 2] = 1
        multiplier[1 : sample_count // 2] = 2
    else:
        multiplier[1 : (sample_count + 1) // 2] = 2
    return np.fft.ifft(np.fft.fft(signal) * multiplier)


def compensate(signal, phase_deg, gain_db):
    gain = 10 ** (gain_db / 20)
    phase = np.deg2rad(phase_deg)
    transformed = analytic_signal(signal) * gain * np.exp(1j * phase)
    return transformed.real, gain


def select_signal(group, packet_index, channel, mode):
    raw, counts = load_group(group)
    if not 0 <= packet_index < len(counts):
        raise RadarError("数据包编号超出范围")
    if not 0 <= channel < 63:
        raise RadarError("接收通道编号超出范围")
    signal = raw[packet_index, channel].copy()
    if mode == "average":
        if signal.size % PERIOD_SAMPLES != 0:
            raise RadarError("记录长度不是 4000 的整数倍，无法周期平均")
        signal = signal.reshape(-1, PERIOD_SAMPLES).mean(axis=0)
    elif mode != "raw":
        raise RadarError("未知波形模式")
    return signal, counts


def downsample_indices(start, stop, maximum):
    count = stop - start
    stride = max(1, math.ceil(count / maximum))
    return np.arange(start, stop, stride, dtype=np.int64), stride


def rounded(values, digits=6):
    return np.round(np.asarray(values), digits).tolist()


def waveform_payload(group, packet_index, channel, mode, phase_deg, gain_db, start, end):
    signal, counts = select_signal(group, packet_index, channel, mode)
    compensated, gain = compensate(signal, phase_deg, gain_db)
    sample_count = signal.size

    if start is None:
        start = 0
    if end is None:
        end = sample_count
    if not 0 <= start < end <= sample_count:
        raise RadarError(f"显示区间必须满足 0 ≤ 起点 < 终点 ≤ {sample_count}")

    indices, stride = downsample_indices(start, end, MAX_DISPLAY_POINTS)
    frequencies = np.fft.rfftfreq(sample_count, d=1 / FS)
    original_spectrum = np.abs(np.fft.rfft(signal))
    compensated_spectrum = np.abs(np.fft.rfft(compensated))
    spectrum_reference = max(float(original_spectrum.max()), 1e-12)
    original_db = 20 * np.log10(np.maximum(original_spectrum / spectrum_reference, 1e-6))
    compensated_db = 20 * np.log10(
        np.maximum(compensated_spectrum / spectrum_reference, 1e-6)
    )
    original_phase = np.rad2deg(np.angle(np.fft.rfft(signal)))
    compensated_phase = np.rad2deg(np.angle(np.fft.rfft(compensated)))

    band = np.flatnonzero((frequencies >= 0) & (frequencies <= FS / 2))
    if band.size > MAX_DISPLAY_POINTS:
        band = band[np.linspace(0, band.size - 1, MAX_DISPLAY_POINTS).astype(int)]

    return {
        "group": group.label,
        "packet": packet_index,
        "packetCount": int(counts[packet_index]),
        "channel": channel,
        "channelLabel": CHANNELS[channel]["label"],
        "mode": mode,
        "sampleRate": FS,
        "sampleCount": sample_count,
        "start": start,
        "end": end,
        "stride": stride,
        "indices": indices.tolist(),
        "original": rounded(signal[indices]),
        "compensated": rounded(compensated[indices]),
        "phaseDeg": phase_deg,
        "gainDb": gain_db,
        "gainLinear": gain,
        "rmsOriginal": float(np.sqrt(np.mean(signal**2))),
        "rmsCompensated": float(np.sqrt(np.mean(compensated**2))),
        "spectrum": {
            "frequencyGHz": rounded(frequencies[band] / 1e9, 6),
            "originalDb": rounded(original_db[band], 4),
            "compensatedDb": rounded(compensated_db[band], 4),
            "originalPhaseDeg": rounded(original_phase[band], 3),
            "compensatedPhaseDeg": rounded(compensated_phase[band], 3),
        },
    }


def query_value(query, name, default=None):
    values = query.get(name)
    return values[-1] if values else default


def query_int(query, name, default=None, minimum=None, maximum=None):
    raw = query_value(query, name)
    if raw is None or raw == "":
        return default
    try:
        value = int(raw)
    except ValueError as error:
        raise RadarError(f"参数 {name} 必须是整数") from error
    if minimum is not None and value < minimum:
        raise RadarError(f"参数 {name} 不能小于 {minimum}")
    if maximum is not None and value > maximum:
        raise RadarError(f"参数 {name} 不能大于 {maximum}")
    return value


def query_float(query, name, default, minimum, maximum):
    raw = query_value(query, name)
    if raw is None or raw == "":
        value = default
    else:
        try:
            value = float(raw)
        except ValueError as error:
            raise RadarError(f"参数 {name} 必须是数值") from error
    if not math.isfinite(value) or not minimum <= value <= maximum:
        raise RadarError(f"参数 {name} 必须位于 {minimum}～{maximum}")
    return value


class RadarHandler(BaseHTTPRequestHandler):
    groups = {}
    index_file = Path(__file__).with_name("index.html")

    def send_bytes(self, content, content_type, status=200):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(content)

    def send_json(self, payload, status=200):
        content = json.dumps(
            payload,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
        ).encode("utf-8")
        self.send_bytes(content, "application/json; charset=utf-8", status)

    def get_group(self, query):
        group_id = query_value(query, "group", "")
        if group_id not in self.groups:
            raise RadarError("请选择有效数据组")
        return self.groups[group_id]

    def do_GET(self):
        try:
            parsed = urlparse(self.path)
            query = parse_qs(parsed.query, keep_blank_values=True)
            if parsed.path in ("/", "/index.html"):
                self.send_bytes(
                    self.index_file.read_bytes(),
                    "text/html; charset=utf-8",
                )
                return
            if parsed.path == "/favicon.ico":
                self.send_response(204)
                self.end_headers()
                return
            if parsed.path == "/api/groups":
                default_group = next(
                    (
                        group.id
                        for group in self.groups.values()
                        if "墙体数据/data1-42cm" in group.id
                    ),
                    next(iter(self.groups)),
                )
                self.send_json(
                    {
                        "groups": [
                            {"id": group.id, "label": group.label}
                            for group in self.groups.values()
                        ],
                        "defaultGroup": default_group,
                    }
                )
                return
            if parsed.path == "/api/meta":
                group = self.get_group(query)
                _, counts = load_group(group)
                self.send_json(
                    {
                        "label": group.label,
                        "packets": [
                            {"index": index, "count": int(count)}
                            for index, count in enumerate(counts)
                        ],
                        "channels": CHANNELS,
                        "sampleCount": 16000,
                        "periodSamples": PERIOD_SAMPLES,
                        "sampleRate": FS,
                    }
                )
                return
            if parsed.path == "/api/waveform":
                group = self.get_group(query)
                packet = query_int(query, "packet", 0, 0, 10000)
                channel = query_int(query, "channel", 0, 0, 62)
                mode = query_value(query, "mode", "average")
                phase = query_float(query, "phase", 0.0, -180.0, 180.0)
                gain = query_float(query, "gain", 0.0, -30.0, 30.0)
                start = query_int(query, "start", None, 0, 1000000)
                end = query_int(query, "end", None, 1, 1000000)
                self.send_json(
                    waveform_payload(
                        group,
                        packet,
                        channel,
                        mode,
                        phase,
                        gain,
                        start,
                        end,
                    )
                )
                return
            self.send_json({"error": "页面不存在"}, 404)
        except RadarError as error:
            self.send_json({"error": str(error)}, 400)
        except (BrokenPipeError, ConnectionResetError):
            return
        except Exception as error:
            self.send_json({"error": f"服务器处理失败：{error}"}, 500)

    def log_message(self, format_string, *args):
        print(f"[{self.log_date_time_string()}] {format_string % args}")


def main():
    parser = argparse.ArgumentParser(description="雷达数据交互查看与相位/强度补偿工具")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="附件根目录")
    parser.add_argument("--port", type=int, default=8765, help="本地端口，默认 8765")
    parser.add_argument("--no-browser", action="store_true", help="启动后不自动打开浏览器")
    args = parser.parse_args()

    root = args.root.expanduser().resolve()
    if not root.is_dir():
        parser.error(f"附件目录不存在：{root}")
    groups = scan_groups(root)
    if not groups:
        parser.error(f"附件目录中没有找到完整数据组：{root}")
    RadarHandler.groups = {group.id: group for group in groups}
    RadarHandler.index_file = Path(__file__).with_name("index.html")

    server = ThreadingHTTPServer(("127.0.0.1", args.port), RadarHandler)
    url = f"http://127.0.0.1:{server.server_address[1]}"
    print(f"已识别 {len(groups)} 个完整数据组")
    print(f"请在浏览器中打开：{url}")
    print("按 Ctrl+C 停止工具")
    if not args.no_browser:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
