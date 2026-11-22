#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""demo_solver.py —— 连接本地 server.py，跑通 LSB Oracle 全流程

逻辑来源（未改攻击逻辑，只加了打印 + 从 banner 读取 coreflame）：
  n 恢复: scripts/你能通过提报的考验吗？/solve_tibao_lsb.py  （c2/c4/c8 的 gcd）
  明文还原: scripts/solve_tibao.py（B 收集 + ceil）

用法:
  py demo_solver.py good   [port]   # 正常版
  py demo_solver.py reversed [port] # 分支反了: bit==1 当下半区
  py demo_solver.py floor  [port]   # 用 floor 还原
"""

import math
import re
import socket
import sys
import time

MODE = sys.argv[1] if len(sys.argv) > 1 else "good"
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 20000
HOST = "127.0.0.1"


def recv_until(sock, marker=b"> "):
    buf = b""
    sock.settimeout(30)
    while marker not in buf:
        chunk = sock.recv(65536)
        if not chunk:
            break
        buf += chunk
    return buf.decode("utf-8", errors="replace")


def fp(x, name):
    h = format(x, "x")
    return f"{name}: bits={x.bit_length():>5}  head={h[:12]}...  tail=...{h[-6:]}"


class Client:
    def __init__(self):
        self.sock = socket.create_connection((HOST, PORT), timeout=30)
        self.f = self.sock.makefile("rwb")
        self.banner = recv_until(self.sock)
        m = re.search(r"coreflame=([0-9a-fA-F]+)", self.banner)
        if not m:
            raise SystemExit("banner 里没有 coreflame")
        self.target = int(m.group(1), 16)
        self.t0 = time.time()

    def divine(self, x):
        self.f.write(f"divine {x:x}\n".encode())
        self.f.flush()
        resp = recv_until(self.sock)
        m = re.search(r"cipher=([0-9a-fA-F]+)", resp)
        if not m:
            raise SystemExit(f"divine 异常: {resp!r}")
        return int(m.group(1), 16)

    def omen(self, c):
        self.f.write(f"omen {c:x}\n".encode())
        self.f.flush()
        resp = recv_until(self.sock)
        m = re.search(r"omen=([01])", resp)
        if not m:
            raise SystemExit(f"omen 异常: {resp!r}")
        return int(m.group(1))

    def close(self):
        try:
            self.f.write(b"leave\n")
            self.f.flush()
        except OSError:
            pass
        self.sock.close()


def strip_small_factors(x, limit=10 ** 6):
    d = 2
    while d < limit:
        while x % d == 0:
            x //= d
        d += 1 if d == 2 else 2
    return x


def main():
    cli = Client()
    print(f"[*] 模式 = {MODE}")
    print("[*] 已连接，banner 收到，coreflame =")
    print("    " + fp(cli.target, "coreflame"))

    # ---------- 1. 三次 divine ----------
    c2 = cli.divine(2)
    c4 = cli.divine(4)
    c8 = cli.divine(8)
    print("\n[1] divine 拿到的三个密文")
    for nm, v in (("c2", c2), ("c4", c4), ("c8", c8)):
        print("    " + fp(v, nm))

    # ---------- 2. 两个差 + gcd ----------
    d1 = c2 * c2 - c4
    d2 = c2 ** 3 - c8
    print("\n[2] 构造两个 n 的倍数")
    print("    " + fp(d1, "c2^2 - c4"))
    print("    " + fp(d2, "c2^3 - c8"))
    g1 = math.gcd(d1, d2)
    n = strip_small_factors(g1)
    print("    " + fp(g1, "gcd(两个差)"))
    print(f"    试除小素数后 n: bits={n.bit_length()}")
    print(f"    校验: d1 % n = {d1 % n}, d2 % n = {d2 % n}")
    print(f"    gcd 比 n 多出的倍数 = {g1 // n}")
    print(f"    [gcd 收敛耗时 {time.time() - cli.t0:.2f}s]")

    # ---------- 3. 2084/2048 次 omen ----------
    k = n.bit_length()
    print(f"\n[3] 开始读 m/n 的二进制位，k = n.bit_length() = {k}")
    B = 0
    lo, hi = 0, n
    c = cli.target
    t1 = time.time()
    for i in range(k):
        c = (c * c2) % n
        bit = cli.omen(c)
        if MODE == "reversed":
            B = (B << 1) | (1 - bit)      # 故意写错：把上半区当成了下半区
        else:
            B = (B << 1) | bit
        mid = (lo + hi) // 2
        if bit:
            lo = mid
        else:
            hi = mid
        if i < 10:
            print(f"    bit[{i:>2}] = {bit}   区间宽 ≈ 2^{(hi - lo).bit_length() - 1:<4}  [{hex(lo)[:10]}..., {hex(hi)[:10]}...]")
        elif (i + 1) % 512 == 0:
            print(f"    ... 已读 {i + 1} 位，区间宽 ≈ 2^{(hi - lo).bit_length() - 1}")
    print(f"    读位耗时 {time.time() - t1:.2f}s；最终区间宽度 = {hi - lo}")
    print(f"    B 的位数 = {B.bit_length()}")

    # ---------- 4. 还原明文 ----------
    if MODE == "floor":
        m = (n * B) >> k                 # 故意写错：floor 而不是 ceil
    else:
        m = (n * B + (1 << k) - 1) >> k  # ceil(n*B/2^k)
    raw = m.to_bytes((m.bit_length() + 7) // 8, "big") if m else b""
    print(f"\n[4] 还原 m（{'floor' if MODE == 'floor' else 'ceil'}）")
    print(f"    m      = {m}")
    print(f"    bytes  = {raw!r}")

    # ---------- 5. 用剩下的一次 divine 验证 ----------
    ok = cli.divine(m) == cli.target
    print(f"\n[5] 验证 divine(m) == coreflame ? {ok}")
    print(f"[*] 总耗时 {time.time() - cli.t0:.2f}s")
    cli.close()


if __name__ == "__main__":
    main()
