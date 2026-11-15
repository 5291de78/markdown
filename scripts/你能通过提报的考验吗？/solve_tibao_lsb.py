# -*- coding: utf-8 -*-
"""
缇宝的考验 —— RSA LSB Oracle 攻击（n、e 均未知）

协议：divine [m_hex] | omen [c_hex] | leave
  divine = 加密 oracle（限 8 次）   : 明文 -> 密文
  omen   = LSB  oracle（限 2100 次）: 密文 -> 明文最低位 0/1

思路：
  1) 恢复 n：利用 (x^e)^2 ≡ x^(2e) (mod n)，即  n | (c_x^2 - c_{x^2})
     n = gcd(c2^2 - c4, c2^3 - c8, c3^2 - c9)，再剥掉小噪声因子
  2) 翻倍因子：c2 = divine(2) 本身就是 2^e mod n —— 全程不需要知道 e
  3) omen 二分恢复明文（先乘翻倍因子再问 bit）：
       bit = lsb(2m mod n) = 0  =>  m < n/2  =>  high = mid
                          = 1  =>  m >= n/2 =>  low  = mid
  4) 用剩余 divine 次数验证候选 low / high
"""
import socket
import math
import re

IP, PORT = "pwn.recruit.yulinsec.cn", 11015

# coreflame（题目给的目标密文）
TARGET_HEX = (
    "1165c7448651807a84b9f28154e994efb6fb1fbc7fd774a4d6c6bed34691040b"
    "365923758c9fa5a4d93b41c24265a2e4c6e18d337077927a23ef59b7c61ad0c6c2a1"
    "b64d57a368f620d1aff6f704564965f44d4b8c7e65c56f4eda6b86c9133d20939c7a"
    "4a9e9a00d0c44be4870561010b4129024d82b07848af33c59063f800b0b5f8b4b3cf"
    "db778b16e19bc2663e3e023d7421a9b5cd748485ed593ae57fa85d59390816c0afe0"
    "bfa9ba68ff5071d6f43aeae7e5105b8e997f79c5e85ba45e5377deab989da7d5c9db"
    "f86025a9e821cf2d0dc090a08647533959de58063df7850bc90586c100ea0e254a6a"
    "63a633553750111c7cab49bab44b230f5267c49f"
)

pat_cipher = re.compile(rb'cipher=([0-9a-fA-F]+)')
pat_omen_left = re.compile(rb'omen_left=\d+')


def send_line(sock, s):
    sock.sendall((str(s) + "\n").encode("utf-8"))


def recv_until(sock, marker=b">", timeout=15):
    """读到提示符 '>' 为止（每次服务器响应以 > 结尾）。"""
    sock.settimeout(timeout)
    buf = b""
    while marker not in buf:
        chunk = sock.recv(4096)
        if not chunk:
            raise ConnectionError("服务器断开连接，缓冲区尾部: %r" % buf[-200:])
        buf += chunk
    return buf


def divine(sock, m_int):
    """加密 oracle：提交明文（int），返回密文（int）。限 8 次。"""
    send_line(sock, "divine %x" % m_int)
    resp = recv_until(sock)
    mm = pat_cipher.search(resp)
    if mm is not None:
        return int(mm.group(1), 16)
    # 兜底：取回包中最长的 hex 串
    hexes = re.findall(rb'[0-9a-fA-F]{16,}', resp)
    if not hexes:
        raise ValueError("divine 回包中找不到密文: %r" % resp)
    return int(max(hexes, key=len), 16)


def omen(sock, c_int, debug=False):
    """LSB oracle：提交密文（int），返回明文最低位 0/1。限 2100 次。"""
    send_line(sock, "omen %x" % c_int)
    resp = recv_until(sock)
    if debug:
        print("[debug] omen 原始回包:", resp)
    cleaned = pat_omen_left.sub(b"", resp)          # 去掉 omen_left=xxxx
    mm = re.search(rb"([01])", cleaned)
    if mm is None:
        raise ValueError("omen 回包中找不到 bit: %r" % resp)
    return int(mm.group(1))


def strip_small_factors(n, limit=10 ** 6):
    """剥掉 gcd 可能附带的小因子（真实 n 是大素数之积，不含小因子）。"""
    d = 2
    while d < limit:
        while n % d == 0:
            n //= d
        d += 1 if d == 2 else 2
    return n


def main():
    sock = socket.create_connection((IP, PORT))
    banner = recv_until(sock)
    print(banner.decode("utf-8", errors="replace"))

    target_c = int(TARGET_HEX, 16)

    # ---------- 第一步：恢复 n（用 5 次 divine） ----------
    c2 = divine(sock, 2)     # = 2^e mod n，同时就是 LSB 攻击的翻倍因子
    c4 = divine(sock, 4)
    c8 = divine(sock, 8)
    c3 = divine(sock, 3)
    c9 = divine(sock, 9)

    n = math.gcd(math.gcd(c2 * c2 - c4, c2 * c2 * c2 - c8), c3 * c3 - c9)
    n = strip_small_factors(n)
    assert n > target_c, "n 恢复异常（比目标密文还小）: %x" % n
    print("[+] n =", hex(n))
    print("[+] n.bit_length() =", n.bit_length())
    print("[+] 2^e mod n = c2 =", hex(c2))

    # ---------- 第二步：LSB oracle 二分恢复明文 ----------
    low, high = 0, n
    c = target_c
    total = n.bit_length()
    for i in range(total):
        c = (c * c2) % n                      # 明文翻倍：等价于 c * 2^e mod n
        bit = omen(sock, c, debug=(i == 0))   # 第一轮打印原始回包以确认格式
        mid = (low + high) // 2
        if bit == 1:
            low = mid                         # m 在上半区
        else:
            high = mid                        # m 在下半区
        if i % 128 == 0:
            print("  [%4d/%d] bit=%d 区间宽≈2^%d"
                  % (i, total, bit, (high - low).bit_length()))
    print("[+] 二分结束，候选区间宽 =", high - low)

    # ---------- 第三步：用剩余 divine 次数验证候选（low / high） ----------
    m = None
    for cand in (low, high):
        if divine(sock, cand) == target_c:
            m = cand
            print("[+] 验证通过：m =", hex(m))
            break
    if m is None:
        print("[!] 验证未命中，兜底取 low（可能 off-by-one）")
        m = low

    flag = m.to_bytes((m.bit_length() + 7) // 8, "big")
    print("[+] m        =", m)
    print("[+] as bytes =", flag)

    send_line(sock, "leave")
    sock.close()


if __name__ == "__main__":
    main()
