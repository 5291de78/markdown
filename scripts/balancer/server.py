#!/usr/bin/env python3
"""怀旧之秤 (crypto-nostalgic-weight) — Recruit 2026 dynamic crypto challenge.

四阶段攻击链:
  Stage 0: 256-bit SWAR popcount 校准（16 计费步）
  Stage 1: Z_256 上 2x2 仿射希尔密码, 已知明文差分攻击（咒绢头 b"CIPHER"）
  Stage 2: 双通道汉明重量二次型滤波 LFSR, u^v 抵消全部二次项后 GF(2) 高斯消元
  Stage 3: 广义 RSA (eu = 1 mod (p-a)(q-a)) + 已知 p+q 高位的修正连分数分解

参考论文:
  - Guimaraes et al., "Nostalgia Cipher: Can Filtered LFSRs Be Secure Again?",
    IACR ePrint 2025/2140 —— Weightwise Quadratic Filter 设计原型
  - Shivarama et al., "From LFSRs to LFGs", IACR ePrint 2026/636
  - Jimenez Urroz, "A new attack to RSA with small private exponent and
    partial information", IACR ePrint 2026/1295
  - Zheng, Nitaj et al., "A Generalized Attack on RSA and Its Variants",
    IACR ePrint 2026/172
"""

import math
import os
import random
import re
import socketserver

FLAG = (
    os.environ.get("YL_DYFLAG")
    or os.environ.get("FLAG")
    or "YulinSec{local_nostalgic_weight_test}"
)

HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "20000"))
CONN_TIMEOUT = 240

# =====================================================================
# Stage 0: 256-bit Hamming Weight Hardware Calibration (16 Steps Max)
# =====================================================================
BITS = 256
REG_MASK = (1 << BITS) - 1
MAX_STEPS = 16
STMT_RE = re.compile(r"([AB])=([AB]|\d+)(\+|-|\*|//|<<|>>|&|\^|%)([AB]|\d+)")


def stage0_calibrate(rf, wf, rng):
    wf.write(
        (
            f"[Stage 0] Calibrate the {BITS}-bit Weightwise Filter unit "
            f"in {MAX_STEPS} steps:\n> "
        ).encode("utf-8")
    )
    wf.flush()
    command = rf.readline(4096).decode(errors="replace").strip()
    if not command:
        return False
    if len(command) > 2500 or not command.endswith(";"):
        return False
    stmts = command[:-1].split(";")
    if not all(STMT_RE.fullmatch(s) for s in stmts):
        return False

    step = MAX_STEPS
    for s in stmts:
        op = s.translate(str.maketrans("", "", "=AB0123456789"))
        if op in (">>", "<<", "+", "-", "&", "^"):
            step -= 1
        elif op in ("*", "//", "%"):
            step -= 3
        else:
            return False

    if step < 0:
        wf.write(b"[-] Step limit exceeded!\n")
        wf.flush()
        return False

    env = {"A": 0, "B": 0}
    for _ in range(100):
        A = rng.randrange(0, 1 << BITS)
        wa = A.bit_count()
        env["A"] = A
        env["B"] = 0
        try:
            for s in stmts:
                exec(s, env)
                env["A"] &= REG_MASK
                env["B"] &= REG_MASK
        except Exception:
            return False
        if env["A"] != wa:
            wf.write(b"[-] Calibration failed!\n")
            wf.flush()
            return False

    wf.write(b"[+] Hardware Weightwise Unit calibrated successfully!\n")
    wf.flush()
    return True


# =====================================================================
# Cryptographic Helpers & Parameters
# =====================================================================
def is_prime(n, rng, k=24):
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n == p:
            return True
        if n % p == 0:
            return False
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for _ in range(k):
        a = rng.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def get_prime(bits, rng):
    while True:
        p = rng.getrandbits(bits) | (1 << (bits - 1)) | 1
        if is_prime(p, rng):
            return p


# Primitive feedback polynomial over GF(2): x^256 + x^10 + x^5 + x^2 + 1
LFSR_TAP = (1 << 10) | (1 << 5) | (1 << 2) | 1
T1_MASK = 0x9E3779B97F4A7C15F39CC0605CEDC8341082276BF3A27251F86C6A11D0C18E95
T2_MASK = 0x6A09E667BB67AE853C6EF372A54FF53A510E527F9B05688C1F83D9AB5BE0CD19
W_MASK = 0x3C6EF372FE94F82BE73980C0B9DB906821044ED7E744E4A3F0D8D423A1831D2B


def lfsr_step(state):
    fb = (state & LFSR_TAP).bit_count() & 1
    return (state >> 1) | (fb << 255)


def generate_nostalgia_stream(seed, n_bytes=36):
    state = seed
    U_bytes, V_bytes = [], []
    for _ in range(n_bytes):
        u_byte, v_byte = 0, 0
        for _ in range(8):
            # Weightwise Quadratic Filter (ePrint 2025/2140)
            w = (state & W_MASK).bit_count()
            wqf_plus = ((w * (w + 1)) // 2) & 1
            wqf_minus = ((w * (w - 1)) // 2) & 1
            u_bit = ((state & T1_MASK).bit_count() & 1) ^ wqf_plus
            v_bit = ((state & T2_MASK).bit_count() & 1) ^ wqf_minus
            u_byte = (u_byte << 1) | u_bit
            v_byte = (v_byte << 1) | v_bit
            state = lfsr_step(state)
        U_bytes.append(u_byte)
        V_bytes.append(v_byte)
    return U_bytes, V_bytes


def affine_hill_encrypt(pairs, K, B):
    out = []
    for x, y in pairs:
        c0 = (K[0][0] * x + K[0][1] * y + B[0]) & 0xFF #255 = mod 256?
        c1 = (K[1][0] * x + K[1][1] * y + B[1]) & 0xFF
        out.append((c0, c1))
    return out


# =====================================================================
# Stage 1-3 Key & Ciphertext Generation + Challenge Session
# =====================================================================
def build_session(rng):
    p = get_prime(512, rng)
    q = get_prime(512, rng)
    N = p * q
    a_off = 7
    Psi = (p - a_off) * (q - a_off)

    while True:
        # u is 340 bits (~N^0.332 > N^0.292), immune to Wiener & Boneh-Durfee
        u = rng.getrandbits(340) | (1 << 339) | 1
        if math.gcd(u, Psi) == 1 and math.gcd(u, (p - 1) * (q - 1)) == 1:
            e = pow(u, -1, Psi)
            if math.gcd(e, (p - 1) * (q - 1)) == 1:
                break

    S = p + q
    shift_bits = S.bit_length() - 256
    seed = S >> shift_bits  # Top 256 MSBs of (p + q)

    c_rsa = pow(int.from_bytes(FLAG.encode(), "big"), e, N)
'''
一段字节数据，按**大端序（big-endian）**拼接成一个十进制整数。
字节从左到右对应整数的高位到低位，和我们日常读写数字的顺序完全一致
把所有字节的十六进制形式首尾拼接，再转换成十进制数
'''
    U_bytes, V_bytes = generate_nostalgia_stream(seed, n_bytes=36)
    header = b"CIPHER"
    header_pairs = [
        (header[0], header[1]),
        (header[2], header[3]),
        (header[4], header[5]),
    ]
    all_pairs = header_pairs + list(zip(U_bytes, V_bytes))

    while True:
        K = [
            [rng.randrange(256), rng.randrange(256)],
            [rng.randrange(256), rng.randrange(256)],
        ]
        if ((K[0][0] * K[1][1] - K[0][1] * K[1][0]) & 1) == 1:
            break
    B = [rng.randrange(256), rng.randrange(256)]
    hill_ct = affine_hill_encrypt(all_pairs, K, B)

    return N, e, a_off, shift_bits, c_rsa, hill_ct


def run_challenge(rf, wf):
    rng = random.SystemRandom()

    if not stage0_calibrate(rf, wf, rng):
        return

    N, e, a_off, shift_bits, c_rsa, hill_ct = build_session(rng)
    wf.write(f"N = {N}\n".encode())
    wf.write(f"e = {e}\n".encode())
    wf.write(f"a_off = {a_off}\n".encode())
    wf.write(f"shift_bits = {shift_bits}\n".encode())
    wf.write(f"c_rsa = {c_rsa}\n".encode())
    wf.write(f"hill_ct = {hill_ct!r}\n".encode())
    wf.write(b"The scale remembers. May your memories carry enough weight.\n")
    wf.flush()


class Handler(socketserver.StreamRequestHandler):
    disable_nagle_algorithm = True
    timeout = CONN_TIMEOUT

    def handle(self):
        try:
            self.request.settimeout(CONN_TIMEOUT)
            run_challenge(self.rfile, self.wfile)
        except Exception:
            try:
                self.wfile.write(b"[-] connection error\n")
            except Exception:
                pass


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


if __name__ == "__main__":
    print(f"nostalgic-weight serving on {HOST}:{PORT}", flush=True)
    Server((HOST, PORT), Handler).serve_forever()
