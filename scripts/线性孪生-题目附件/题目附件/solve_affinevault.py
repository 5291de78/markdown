# -*- coding: utf-8 -*-
"""
AffineVault 攻击脚本：ECDSA 仿射 nonce 关联 (k2 = a*k1 + b, 16-bit trim 空间)
用法: py solve.py <host> <port>
nc pwn.recruit.yulinsec.cn 11096
"""
import socket
import sys
import time
from cryptography.hazmat.primitives.asymmetric.ec import (
    derive_private_key, SECP256K1,
)
from cryptography.hazmat.primitives.asymmetric.utils import (
    decode_dss_signature, encode_dss_signature,
)

FIELD = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
GX = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
GY = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8


def recv_until(sock, token=b"private_key_hex> "):
    buf = b""
    while token not in buf:
        chunk = sock.recv(4096)
        if not chunk:
            break
        buf += chunk
    return buf.decode()


def parse(transcript):
    kv = {}
    for line in transcript.splitlines():
        if "=" in line:
            k, _, v = line.partition("=")
            kv[k.strip()] = v.strip()
    x = int(kv["pubkey"][2:66], 16)
    y = int(kv["pubkey"][66:130], 16)
    z1, r1, s1 = (int(kv[f"record[0].{f}"], 16) for f in ("hash", "r", "s"))
    z2, r2, s2 = (int(kv[f"record[1].{f}"], 16) for f in ("hash", "r", "s"))
    return (x, y), (z1, r1, s1), (z2, r2, s2)


def pub_of(d):
    """d*G，返回 (x, y)"""
    priv = derive_private_key(d, SECP256K1())
    nums = priv.public_key().public_numbers()
    return nums.x, nums.y


def solve(q, sig1, sig2):
    """枚举 2^16 个 trim，解线性方程得 d 候选，验 d*G == Q"""
    n = ORDER
    z1, r1, s1 = sig1
    z2, r2, s2 = sig2
    qx, qy = q
    s1s2 = s1 * s2 % n
    for trim in range(1 << 16):
        a = 2 + (trim >> 11)          # multiplier ∈ [2, 33]
        b = trim & 0x7FF              # offset   ∈ [0, 2047]
        den = (s1 * r2 - a * s2 * r1) % n
        if den == 0:
            continue
        num = (a * s2 * z1 - s1 * z2 + b * s1s2) % n
        d = num * pow(den, -1, n) % n
        if d == 0:
            continue
        # 关键外部校验：d*G 是否等于公钥
        if pub_of(d) == (qx, qy):
            return d, trim, (a, b)
    return None, None, None


def main():
    '''
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 20000
    '''
    host = 'pwn.recruit.yulinsec.cn'
    port = 11042


    t0 = time.time()
    sock = socket.create_connection((host, port), timeout=30)
    transcript = recv_until(sock)
    q, sig1, sig2 = parse(transcript)
    print(f"[+] 公钥与双签名到手 ({time.time()-t0:.1f}s)，开始枚举 2^16 个 ladder...")

    d, trim, (a, b) = solve(q, sig1, sig2)
    if d is None:
        print("[-] 未找到，检查解析是否正确")
        return
    print(f"[+] 命中! trim={trim} (a={a}, b={b})")
    print(f"[+] 私钥 d = {hex(d)}  (耗时 {time.time()-t0:.1f}s)")

    sock.sendall(f"{d:x}\n".encode())
    resp = sock.recv(4096).decode()
    print("[+] 服务端响应:", resp.strip())
    sock.close()


if __name__ == "__main__":
    main()
