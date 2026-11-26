#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""本地复现「你能通过提报的考验吗」服务端（RSA LSB Oracle 题）

=====================================================================
启动
----
    py server.py                          # 默认 127.0.0.1:20000
    $env:PORT=20001; py server.py         # 换端口
    $env:YL_DYFLAG='YulinSec{my_flag}'; py server.py

可选环境变量（只有本地演示才用，默认值就是题面限制）：
    HOST           监听地址，默认 127.0.0.1
    PORT           监听端口，默认 20000
    DIVINE_LIMIT   divine 次数上限，默认 8
    OMEN_LIMIT     omen   次数上限，默认 2100

连接
----
    nc 127.0.0.1 20000
    或在 Python 里 socket.create_connection(("127.0.0.1", 20000))

协议
----
    divine <m_hex>   加密，返回 cipher=<c_hex>                     限 8 次
    omen   <c_hex>   解密并返回结果最低位，返回 omen=<0|1>
                     以及 omen_left=<剩余次数>                      限 2100 次
    leave            主动断开

任何非法输入（不是十六进制、未知指令、次数用尽）都返回一行
"[-] ..." 错误信息并继续等待输入，不会直接把连接掐掉。
=====================================================================
"""

import math
import os
import random
import socketserver
import sys
import time

HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "20000"))
DIVINE_LIMIT = int(os.environ.get("DIVINE_LIMIT", "8"))
OMEN_LIMIT = int(os.environ.get("OMEN_LIMIT", "2100"))
HANDLER_TIMEOUT = 300

FLAG = (os.environ.get("YL_DYFLAG") or "YulinSec{local_lsb_oracle_demo}").strip()

# ---------------------------------------------------------------- 素数
SMALL_PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)


def is_prime(x: int, rounds: int = 24) -> bool:
    """Miller-Rabin。本地演示够用。"""
    if x < 2:
        return False
    for p in SMALL_PRIMES:
        if x % p == 0:
            return x == p
    d, s = x - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for _ in range(rounds):
        a = random.randrange(2, x - 1)
        v = pow(a, d, x)
        if v == 1 or v == x - 1:
            continue
        for _ in range(s - 1):
            v = v * v % x
            if v == x - 1:
                break
        else:
            return False
    return True


def gen_prime(bits: int) -> int:
    while True:
        x = random.getrandbits(bits) | (1 << (bits - 1)) | 1
        if is_prime(x):
            return x


def make_key():
    """两个 1024 位素数；e 取 9~16 位（题面提示「九位往上，十六位封顶」）。"""
    while True:
        p, q = gen_prime(1024), gen_prime(1024)
        if p == q:
            continue
        n = p * q
        phi = (p - 1) * (q - 1)
        while True:
            e = random.randrange(1 << 8, 1 << 16) | 1   # 256..65535 -> 9~16 位
            if 9 <= e.bit_length() <= 16 and math.gcd(e, phi) == 1:
                break
        d = pow(e, -1, phi)
        return p, q, n, e, d


T_GEN0 = time.time()
P, Q, N, E, D = make_key()
M = int.from_bytes(FLAG.encode("utf-8"), "big")
C = pow(M, E, N)          # 题目给玩家的 coreflame
assert M < N, "flag 太长，超出了模数"


def banner() -> str:
    return (
        "==================== 一线天机 ====================\n"
        "白厄穿过旋门，踏入天机圣所。缇宝捧着一卷无字的谶语，\n"
        "赛飞儿坐在门槛上，慢悠悠地晃着一串不知真假的钥匙。\n"
        "\n"
        "缇宝：「火种之印已封入谶语。天机万卷，只露一线。」\n"
        f"coreflame={C:x}\n"
        "赛飞儿：「想求签？本小姐的戏法一场只演 "
        f"{DIVINE_LIMIT} 次。\n"
        "        想问天机？缇宝最多奉陪 "
        f"{OMEN_LIMIT} 次，问完谶语就自己合上。\n"
        "        哦，提示只有一个——我偷走的那枚指数，\n"
        "        九位往上，十六位封顶。」\n"
        "\n"
        "指令：divine [m_hex] | omen [c_hex] | leave\n"
        "> "
    )


class Handler(socketserver.StreamRequestHandler):
    def send(self, text: str) -> None:
        self.wfile.write(text.encode("utf-8"))
        self.wfile.flush()

    def handle(self) -> None:
        self.request.settimeout(HANDLER_TIMEOUT)
        divine_used = 0
        omen_used = 0
        self.send(banner())
        while True:
            try:
                raw = self.rfile.readline(4096)
            except OSError:
                return
            if not raw:
                return
            line = raw.decode("utf-8", errors="replace").strip()
            if not line:
                self.send("> ")
                continue

            parts = line.split()
            cmd = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else ""

            if cmd in ("leave", "exit", "quit"):
                self.send("[-] 谶语已合上。\n")
                return

            if cmd not in ("divine", "omen"):
                self.send("[-] 未知指令，可用：divine <m_hex> | omen <c_hex> | leave\n> ")
                continue

            if len(parts) != 2:
                self.send("[-] 参数个数不对，格式：<指令> <hex>\n> ")
                continue

            try:
                value = int(arg, 16)
            except ValueError:
                self.send("[-] 参数不是合法的十六进制数\n> ")
                continue
            if value < 0:
                self.send("[-] 参数必须是非负数\n> ")
                continue

            if cmd == "divine":
                if divine_used >= DIVINE_LIMIT:
                    self.send(f"[-] 戏法已用尽（{DIVINE_LIMIT}/{DIVINE_LIMIT}）\n> ")
                    continue
                divine_used += 1
                self.send(f"cipher={pow(value, E, N):x}\n"
                          f"divine_left={DIVINE_LIMIT - divine_used}\n> ")
            else:
                if omen_used >= OMEN_LIMIT:
                    self.send(f"[-] 天机已问尽（{OMEN_LIMIT}/{OMEN_LIMIT}）\n> ")
                    continue
                omen_used += 1
                bit = pow(value, D, N) & 1
                self.send(f"omen={bit}\n"
                          f"omen_left={OMEN_LIMIT - omen_used}\n> ")


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True
    request_queue_size = 64


def main() -> None:
    print("[*] 正在生成两把 1024 位素数 ...", flush=True)
    print(f"[+] p 位数 = {P.bit_length()}，q 位数 = {Q.bit_length()}", flush=True)
    print(f"[+] n     = {N:x}", flush=True)
    print(f"[+] n.bit_length() = {N.bit_length()}", flush=True)
    print(f"[+] e     = {E}  ({E.bit_length()} bits)", flush=True)
    print(f"[*] e 是否落在题面 9~16 位范围: {'YES' if 9 <= E.bit_length() <= 16 else 'NO'}", flush=True)
    print(f"[+] 目标明文 = {FLAG}  (demo 用，正式题不会给)", flush=True)
    print(f"[+] coreflame = {C:x}", flush=True)
    print(f"[*] 密钥生成耗时 {time.time() - T_GEN0:.2f}s", flush=True)
    print(f"[*] listening on {HOST}:{PORT}  (divine<={DIVINE_LIMIT}, omen<={OMEN_LIMIT})", flush=True)
    with Server((HOST, PORT), Handler) as srv:
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            print("[*] bye", flush=True)


if __name__ == "__main__":
    sys.exit(main())
