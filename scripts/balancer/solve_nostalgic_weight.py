#!/usr/bin/env python3
# solve_nostalgic_weight.py — 怀旧之秤 全自动 exploit（本地/远程通用）
import socket, re, ast, sys
from math import isqrt

# ===== 题目常量（来自 server.py）=====
T1 = 0x9E3779B97F4A7C15F39CC0605CEDC8341082276BF3A27251F86C6A11D0C18E95
T2 = 0x6A09E667BB67AE853C6EF372A54FF53A510E527F9B05688C1F83D9AB5BE0CD19
WM = 0x3C6EF372FE94F82BE73980C0B9DB906821044ED7E744E4A3F0D8D423A1831D2B
TAP = (1 << 10) | (1 << 5) | (1 << 2) | 1      # x^256+x^10+x^5+x^2+1 抽头多项式
REG = (1 << 256) - 1
MASK = T1 ^ T2 ^ WM   # u⊕v 之后二次项抵消，剩下的线性掩码

# ===== Stage 0: SWAR popcount，15 步（预算 16）=====
def stage0_payload():
    M1 = int('5' * 64, 16)      # 0x5555...  2位字段掩码 0101 0101 0101

    M2 = int('3' * 64, 16)      # 0x3333...  4位字段掩码
    M8 = int('0F' * 32, 16)     # 0x0F0F...  8位字段掩码

    K8 = int('01' * 32, 16)     # 0x0101...01  32个字节槽求和到顶字节host
    return (f"B=A>>1;B=B&{M1};A=A-B;"          # 折叠到 2 位字段（每字段 <=2）
            # 为什么是A = A - B 每两个位有0 ，1 ， 2
            f"B=A>>2;B=B&{M2};A=A&{M2};A=A+B;" # 折叠到 4 位字段（<=4）
            f"B=A>>4;B=B&{M8};A=A&{M8};A=A+B;" # 折叠到 8 位字段（<=8）
            f"A=A*{K8};A=A>>248;")             # 乘法和进顶字节，>>248 取出

# ===== 网络 =====
def recv_until(sock, marker):
    buf = b''
    while marker not in buf:
        chunk = sock.recv(4096)
        if not chunk:
            break
        buf += chunk
    return buf

def get_session(host, port):
    s = socket.create_connection((host, port), timeout=300)
    recv_until(s, b'> ')
    s.sendall(stage0_payload().encode() + b'\n')
    data = recv_until(s, b'weight.')
    while True:                     # 读到 EOF（服务端发完就断开）
        try:
            chunk = s.recv(4096)
        except socket.timeout:
            break
        if not chunk:
            break
        data += chunk
    text = data.decode()
    print(text)
    assert 'calibrated successfully' in text, 'Stage 0 校准失败: ' + text
    grab = lambda k: int(re.search(rf'{k} = (\d+)', text).group(1))
    hill_ct = ast.literal_eval(re.search(r'hill_ct = (\[.*\])', text).group(1))
    return grab('N'), grab('e'), grab('a_off'), grab('shift_bits'), grab('c_rsa'), hill_ct

# ===== Stage 1: Z_256 仿射 Hill，已知明文差分 =====
def inv2(M, mod=256):                       # det 必须为奇
    a, b = M[0]; c, d = M[1]
    di = pow((a * d - b * c) % mod, -1, mod)
    return [[d * di % mod, -b * di % mod], [-c * di % mod, a * di % mod]]

def mm2(A, B):
    return [[(A[i][0] * B[0][j] + A[i][1] * B[1][j]) % 256 for j in (0, 1)] for i in (0, 1)]
#二阶矩阵在mod256下的计算 <==> A x B

def vm2(r, M):                              # 行向量 × 矩阵
    return [(r[0] * M[0][j] + r[1] * M[1][j]) % 256 for j in (0, 1)]
#

def stage1(hill_ct):
    X = [(67, 73), (80, 72), (69, 82)]      # "CI" "PH" "ER"
    Y = [tuple(p) for p in hill_ct[:3]]
    Md = [[(X[1][j] - X[0][j]) % 256 for j in (0, 1)],
          [(X[2][j] - X[1][j]) % 256 for j in (0, 1)]]
    Cd = [[(Y[1][j] - Y[0][j]) % 256 for j in (0, 1)],
          [(Y[2][j] - Y[1][j]) % 256 for j in (0, 1)]]
    W = mm2(inv2(Md), Cd)                   # C_delta = M_delta · W  →  W = M_delta^-1 · C_delta
    Wi = inv2(W)
    B = [(Y[0][j] - vm2(X[0], W)[j]) % 256 for j in (0, 1)]
    pairs = [vm2([(c[j] - B[j]) % 256 for j in (0, 1)], Wi) for c in hill_ct]
    assert [tuple(p) for p in pairs[:3]] == X, 'Stage1 自检失败'
    return pairs

# ===== Stage 2: u⊕v 消二次项 + GF(2) 高斯消元 =====
def gf2_solve(eqs):
    basis = {}                              # pivot 位 -> 增广行（bit0 是 rhs）
    for coeffs, rhs in eqs:
        x = (coeffs << 1) | rhs
        while x:
            p = x.bit_length() - 1
            if p == 0:
                if x & 1:
                    raise ValueError('矛盾方程')
                break
            if p in basis:
                x ^= basis[p]
            else:
                basis[p] = x
                break
    sol = 0
    for p in sorted(basis):                 # 回代：pivot 是行内最高位
        row = basis[p]
        if (row & 1) ^ (((row >> 1) & sol).bit_count() & 1):
            sol |= 1 << (p - 1)
    return sol

def stage2(pairs):
    obs = [((u >> b) ^ (v >> b)) & 1 for u, v in pairs[3:] for b in range(7, -1, -1)]
    eqs = []
    m = MASK                                # bit_t = parity(m_t & seed)
    for bit in obs:                         # 掩码回拉演化（LFSR 的线性对偶）
        eqs.append((m, bit))
        m = ((m << 1) & REG) ^ (TAP if (m >> 255) & 1 else 0)
    seed = gf2_solve(eqs)
    m = MASK                                # 全部 288 个方程逐一验证
    for bit in obs:
        assert ((m & seed).bit_count() & 1) == bit, 'Stage2 验证失败'
        m = ((m << 1) & REG) ^ (TAP if (m >> 255) & 1 else 0)
    return seed

#seed就是 p + q 的 top256 MSB

# ===== Stage 3: 广义 RSA + 连分数（Legendre）=====
def convergents(num, den):                  # e/Psi0 的渐近分数 (k, u)
    h2, h1, k2, k1 = 0, 1, 1, 0
    while den:
        a = num // den
        h2, h1 = h1, a * h1 + h2
        k2, k1 = k1, a * k1 + k2
        num, den = den, num - a * den
        yield h1, k1

def stage3(N, e, a_off, shift_bits, c_rsa, seed):
    Psi0 = N - a_off * (seed << shift_bits) + a_off * a_off
    for k, u in convergents(e, Psi0):
        if k == 0 or (e * u - 1) % k:
            continue
        Psi = (e * u - 1) // k
        rem = N + a_off * a_off - Psi       # = a_off * S
        if rem % a_off:
            continue
        S = rem // a_off
        D = S * S - 4 * N                   # x^2 - Sx + N = 0 的判别式
        if D < 0:
            continue
        r = isqrt(D)
        if r * r != D:
            continue
        p, q = (S + r) // 2, (S - r) // 2
        if p * q == N:
            # 分解成功即可用标准 RSA 私钥解密（服务器保证了 gcd(e,(p-1)(q-1))=1）
            d = pow(e, -1, (p - 1) * (q - 1))
            m = pow(c_rsa, d, N)
            return m.to_bytes((m.bit_length() + 7) // 8, 'big')
    return None

def main():
    host, port = "127.0.0.1" , 20000
    print('[*] 连接，提交 Stage 0 校准程序 ...')
    N, e, a_off, shift_bits, c_rsa, hill_ct = get_session(host, port)
    print('[+] Stage 0 通过，参数到手')
    pairs = stage1(hill_ct)
    print('[+] Stage 1 完成：Hill 破解，恢复 U/V 双流')
    seed = stage2(pairs)
    print(f'[+] Stage 2 完成：seed（S 的高 256 位）= {hex(seed)}')
    flag = stage3(N, e, a_off, shift_bits, c_rsa, seed)
    assert flag, 'Stage 3 失败'
    print(f'[+] Stage 3 完成：flag = {flag.decode()}')

if __name__ == '__main__':
    main()
