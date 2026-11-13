#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RSA 加密 / 解密工具（纯 Python 实现，无第三方依赖）

功能：
  1. gen  生成 RSA 密钥对
  2. enc  使用公钥加密（支持文本字符串或任意文件）
  3. dec  使用私钥解密

用法示例：
  python rsa_tool.py gen -b 1024
  python rsa_tool.py enc -n <N(hex)> -e 65537 -t "hello rsa"
  python rsa_tool.py dec -n <N(hex)> -d <D(hex)> -c <密文hex>
  python rsa_tool.py enc -n <N(hex)> -e 65537 -i 1.txt -o 1.enc
  python rsa_tool.py dec -n <N(hex)> -d <D(hex)> -i 1.enc -o 1.out.txt

说明：
  这是用于学习 RSA 数学原理的实现（大素数生成、模逆元、快速模幂、
  Miller-Rabin 素性检测、分块加解密）。
  生产环境请使用 cryptography / pycryptodome 等经过审计的库，并配合 OAEP 填充。
"""

import argparse
import random
import sys


# ---------------------------------------------------------------------------
# 一、数论基础
# ---------------------------------------------------------------------------

def gcd(a, b):
    """欧几里得算法求最大公约数"""
    while b:
        a, b = b, a % b
    return a


def egcd(a, b):
    """扩展欧几里得算法：返回 (g, x, y)，满足 g = a*x + b*y = gcd(a, b)"""
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1
    while r:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
        old_t, t = t, old_t - q * t
    return old_r, old_s, old_t


def modinv(a, m):
    """求 a 在模 m 下的乘法逆元（要求 gcd(a, m) = 1）"""
    g, x, _ = egcd(a, m)
    if g != 1:
        raise ValueError(f"逆元不存在：gcd({a}, {m}) = {g} != 1")
    return x % m


# ---------------------------------------------------------------------------
# 二、素性检测与素数生成
# ---------------------------------------------------------------------------

_SMALL_PRIMES = [
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61,
    67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131,
]


def is_prime(n, rounds=40):
    """Miller-Rabin 素性检测（概率算法，rounds 越大误判率越低）"""
    if n < 2:
        return False
    for p in _SMALL_PRIMES:
        if n % p == 0:
            return n == p

    # 把 n-1 写作 d * 2^s，其中 d 为奇数
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1

    for _ in range(rounds):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)  # pow 三参数 = 快速模幂 a^d mod n
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def gen_prime(bits):
    """随机生成一个 bits 位的素数"""
    while True:
        n = random.getrandbits(bits)
        n |= (1 << (bits - 1)) | 1  # 置最高位保证位数、置最低位保证奇数
        if any(n % p == 0 for p in _SMALL_PRIMES):
            continue
        if is_prime(n):
            return n


# ---------------------------------------------------------------------------
# 三、RSA 核心
# ---------------------------------------------------------------------------

def generate_keypair(bits=1024, e=65537):
    """
    生成密钥对。返回 (公钥, 私钥, 密钥参数)。
      公钥 = (n, e)，私钥 = (n, d)，参数 = (p, q, phi)
    """
    if bits < 16:
        raise ValueError("密钥位数过小，至少 16 位")
    while True:
        p = gen_prime(bits // 2)
        q = gen_prime(bits - bits // 2)
        n = p * q
        phi = (p - 1) * (q - 1)
        if gcd(e, phi) == 1:  # e 必须与 φ(n) 互素才有逆元 d
            break
        # 极少数情况下 e 与 φ(n) 不互素，重新生成 p、q 即可
    d = modinv(e, phi)
    return (n, e), (n, d), (p, q, phi)


def encrypt_int(m, pub):
    """加密单个整数：c = m^e mod n"""
    n, e = pub
    if not 0 <= m < n:
        raise ValueError(f"明文需满足 0 <= m < n，当前 m 超范围（n 位数为 {n.bit_length()}）")
    return pow(m, e, n)


def decrypt_int(c, priv):
    """解密单个整数：m = c^d mod n"""
    n, d = priv
    if not 0 <= c < n:
        raise ValueError("密文需满足 0 <= c < n")
    return pow(c, d, n)


# ---------------------------------------------------------------------------
# 四、任意字节数据的加解密（分块）
# ---------------------------------------------------------------------------

def _block_size(n):
    """每个明文块最多容纳的字节数，保证块值 < n"""
    return max(1, (n.bit_length() - 1) // 8)


def encrypt_bytes(data, pub):
    """
    加密任意字节串（分块）。返回密文字节串。
    头 8 字节记录明文长度；最后一个块不足补 0。
    """
    n, e = pub
    bs = _block_size(n)
    csize = (n.bit_length() + 7) // 8  # 每个密文块的固定字节宽

    payload = len(data).to_bytes(8, "big") + data
    payload += b"\x00" * ((-len(payload)) % bs)

    out = bytearray()
    for i in range(0, len(payload), bs):
        m = int.from_bytes(payload[i:i + bs], "big")
        c = pow(m, e, n)
        out += c.to_bytes(csize, "big")
    return bytes(out)


def decrypt_bytes(data, priv):
    """解密 encrypt_bytes 的输出，还原原始字节串"""
    n, d = priv
    bs = _block_size(n)
    csize = (n.bit_length() + 7) // 8

    if len(data) % csize != 0:
        raise ValueError("密文长度不正确")

    payload = bytearray()
    for i in range(0, len(data), csize):
        c = int.from_bytes(data[i:i + csize], "big")
        m = pow(c, d, n)
        payload += m.to_bytes(bs, "big")

    length = int.from_bytes(payload[:8], "big")
    return bytes(payload[8:8 + length])


def encrypt_text(text, pub):
    """加密文本（UTF-8），返回十六进制密文字符串"""
    return encrypt_bytes(text.encode("utf-8"), pub).hex()


def decrypt_text(hex_cipher, priv):
    """解密十六进制密文，返回 UTF-8 文本"""
    return decrypt_bytes(bytes.fromhex(hex_cipher), priv).decode("utf-8")


# ---------------------------------------------------------------------------
# 五、命令行
# ---------------------------------------------------------------------------

def _print_key(pub, priv, params, show_primes):
    (n, e) = pub
    (_, d) = priv
    p, q, phi = params
    print("公钥 (n, e):")
    print(f"  n = {n:x}")
    print(f"  e = {e}")
    print("私钥 (n, d):")
    print(f"  d = {d:x}")
    if show_primes:
        print("密钥参数（请妥善保管，切勿泄露）:")
        print(f"  p = {p:x}")
        print(f"  q = {q:x}")
        print(f"  phi = {phi:x}")


def _output_cipher(ct, outfile):
    hx = ct.hex()
    if outfile:
        with open(outfile, "w") as f:
            f.write(hx)
        print(f"密文已写入 {outfile}", file=sys.stderr)
    else:
        print(hx)


def _output_plain(data, outfile):
    if outfile:
        with open(outfile, "wb") as f:
            f.write(data)
        print(f"明文已写入 {outfile}", file=sys.stderr)
    else:
        try:
            print(data.decode("utf-8"))
        except UnicodeDecodeError:
            print(data.hex())


def main():
    parser = argparse.ArgumentParser(description="RSA 加密/解密工具（纯 Python）")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_gen = sub.add_parser("gen", help="生成密钥对")
    p_gen.add_argument("-b", "--bits", type=int, default=1024, help="密钥长度（默认 1024）")
    p_gen.add_argument("-e", "--exponent", type=int, default=65537, help="公钥指数 e（默认 65537）")
    p_gen.add_argument("--primes", action="store_true", help="同时输出 p、q、φ(n)")

    p_enc = sub.add_parser("enc", help="用公钥加密")
    p_enc.add_argument("-n", required=True, help="模数 n（十六进制）")
    p_enc.add_argument("-e", type=int, required=True, help="公钥指数 e")
    p_enc.add_argument("-t", "--text", help="待加密文本")
    p_enc.add_argument("-i", "--in", dest="infile", help="待加密文件")
    p_enc.add_argument("-o", "--out", help="密文输出文件（默认打印到终端）")

    p_dec = sub.add_parser("dec", help="用私钥解密")
    p_dec.add_argument("-n", required=True, help="模数 n（十六进制）")
    p_dec.add_argument("-d", required=True, help="私钥指数 d（十六进制）")
    p_dec.add_argument("-c", "--cipher", help="密文（十六进制）")
    p_dec.add_argument("-i", "--in", dest="infile", help="密文文件（内容为十六进制）")
    p_dec.add_argument("-o", "--out", help="明文输出文件")

    args = parser.parse_args()

    if args.cmd == "gen":
        print(f"正在生成 {args.bits} 位密钥 ...", file=sys.stderr)
        pub, priv, params = generate_keypair(args.bits, args.exponent)
        _print_key(pub, priv, params, args.primes)
        return

    if args.cmd == "enc":
        n = int(args.n, 16)
        pub = (n, args.e)
        if args.infile:
            with open(args.infile, "rb") as f:
                data = f.read()
            ct = encrypt_bytes(data, pub)
        elif args.text is not None:
            ct = encrypt_bytes(args.text.encode("utf-8"), pub)
        else:
            parser.error("请通过 -t 或 -i 提供明文")
        _output_cipher(ct, args.out)
        return

    if args.cmd == "dec":
        n = int(args.n, 16)
        d = int(args.d, 16)
        priv = (n, d)
        if args.infile:
            with open(args.infile) as f:
                hex_cipher = f.read().strip()
        elif args.cipher is not None:
            hex_cipher = args.cipher
        else:
            parser.error("请通过 -c 或 -i 提供密文")
        data = decrypt_bytes(bytes.fromhex(hex_cipher), priv)
        _output_plain(data, args.out)
        return


if __name__ == "__main__":
    main()