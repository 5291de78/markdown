import socket, re, math
from Crypto.Util.number import long_to_bytes

IP = "pwn.recruit.yulinsec.cn"
PORT = 11057

def recv_until(sock, marker=b"> "):
    data = b""
    while marker not in data:
        chunk = sock.recv(4096)
        if not chunk:
            break
        data += chunk
    return data.decode(errors="replace")

def send_line(sock, s):
    sock.sendall((str(s) + "\n").encode("utf-8"))

def main():
    sock = socket.socket()
    sock.connect((IP, PORT))

    banner = recv_until(sock)
    print(banner)
    core = int(re.search(r'coreflame=([0-9a-fA-F]+)', banner).group(1), 16)

    def divine(m):
        send_line(sock, "divine " + format(m, "x"))
        return int(re.search(r'cipher=([0-9a-fA-F]+)', recv_until(sock)).group(1), 16)

    def omen(c):
        send_line(sock, "omen " + format(c, "x"))
        return int(re.search(r'omen=([01])', recv_until(sock)).group(1))

    # 恢复 n：m1^e * m2^e == (m1*m2)^e (mod n)，用差值的 gcd 提取 n
    c2 = divine(2)
    c3 = divine(3)
    c4 = divine(4)
    c6 = divine(6)
    c8 = divine(8)
    c9 = divine(9)

    n = math.gcd(c4 - c2*c2, c6 - c2*c3)
    n = math.gcd(n, c8 - c2*c4)
    n = math.gcd(n, c9 - c3*c3)
    for p in (2, 3, 5, 7):
        while n % p == 0:
            n //= p
    print("n =", n)
    print("n.bit_length() =", n.bit_length())

    # 恢复 e：提示说 9~16 位，暴力枚举
    e = None
    for cand in range(1, 65536):
        if pow(2, cand, n) == c2:
            e = cand
            break
    print("e =", e)
    print("验证 3^e mod n == c3 :", pow(3, e, n) == c3)

    # LSB oracle 攻击：逐位收集 m/n 的二进制位，还原明文
    k = n.bit_length()
    pow2 = pow(2, e, n)
    c = core
    B = 0
    for i in range(k):
        c = (c * pow2) % n
        B = (B << 1) | omen(c)
        if i % 256 == 0:
            print("progress", i, "/", k)

    m = (n * B + (1 << k) - 1) >> k   # m = ceil(n * B / 2^k)
    flag = long_to_bytes(m)
    print("FLAG =", flag)

    send_line(sock, "leave")
    sock.close()

main()