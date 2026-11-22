import random as rng

N = 72491232585254304790092011170191491506118029954174838203525589961848318609182548810051238350877965632889112291722250103736125424144097724743068200255471317893228430445420023262510539583155431495121304581964686177675631867164133890587397259280512357598719740549574500156737375368034409269883693751367157284157
e = 39943082387012276223064337754929594169598475948707265252663859611418078248271313407443146106158507562686702014117871316968424253045702288026755535441467013857514599198231948570095505709670084775602141835941291607693896056011485199766334522139276197050202399282798326171885206097778243119294567198768705914793
a_off = 7
shift_bits = 257
c_rsa = 31252850521063384900087784484896156451826776659246132014357328196862076759381274507887823344401207791419933274234746885526370606114708843433873076111105897541521024877438861263389090356748058064390499020681555828958234862930920976700892578490553474584545977672809390205844282605483209598635564932391252898040
hill_ct = [(71, 34), (146, 38), (149, 9), (233, 200), (153, 5), (156, 1), (96, 83), (23, 143), (255, 183), (44, 46), (79, 237), (161, 245), (86, 70), (152, 166), (35, 98), (236, 64), (170, 133), (39, 87), (152, 226), (65, 72), (236, 113), (156, 252), (178, 142), (159, 177), (68, 195), (23, 180), (215, 21), (28, 119), (50, 101), (117, 72), (67, 59), (28, 32), (62, 204), (230, 26), (148, 235), (11, 75), (121, 202), (100, 75), (54, 248)]


# ===== Stage 0: SWAR popcount，15 步（预算 16）=====
def stage0_payload():
    M1 = int('5' * 64, 16)      # 0x5555...  2位字段掩码
    M2 = int('3' * 64, 16)      # 0x3333...  4位字段掩码
    M8 = int('0F' * 32, 16)     # 0x0F0F...  8位字段掩码
    K8 = int('01' * 32, 16)     # 0x0101...01  32个字节槽求和到顶字节host
    return (f"B=A>>1;B=B&{M1};A=A-B;"          # 折叠到 2 位字段（每字段 <=2）
            f"B=A>>2;B=B&{M2};A=A&{M2};A=A+B;" # 折叠到 4 位字段（<=4）
            f"B=A>>4;B=B&{M8};A=A&{M8};A=A+B;" # 折叠到 8 位字段（<=8）
            f"A=A*{K8};A=A>>248;")             # 乘法和进顶字节，>>248 取出


#======================[STAGE1]============================
#希尔密码映射
def mm2(A,B):
    return [[(A[i][0] * B[0][j] + A[i][1] * B[1][j]) & 0xFF for j in range(2)]for i in range(2)]

def revm2(A): #mod256下你逆矩阵的求解
    det = (A[0][0] * A[1][1] - A[0][1] * A[1][0]) & 0xFF
    assert det%2 == 1
    revm = [[A[1][1] , -A[0][1]] , [-A[1][0] , A[0][0]]]
    idet = pow(det, -1, 256)
    return [[(A[1][1] * idet) & 0xFF, (-A[0][1] * idet) & 0xFF],
            [(-A[1][0] * idet) & 0xFF, (A[0][0] * idet) & 0xFF]]

def affine_hill_encrypt(pairs, K, B):
    out = []
    for x, y in pairs:
        c0 = (K[0][0] * x + K[0][1] * y + B[0]) & 0xFF #255 = mod 256?
        c1 = (K[1][0] * x + K[1][1] * y + B[1]) & 0xFF
        out.append((c0, c1))
    return out

def vm2(m , K):
    return [(m[0] * K[0][0] + m[1] * K[1][0])& 0xFF , (m[0] * K[0][1] + m[1] * K[1][1])& 0xFF]

def transpose(A):
    return [[A[0][0], A[1][0]], [A[0][1], A[1][1]]]

header = b"CIPHER"
header_pairs = [
    (header[0], header[1]),
    (header[2], header[3]),
    (header[4], header[5]),
]

message = "idontknow4"
message_pairs = [ (ord(message[i]) , ord(message[i + 1]) ) for i in range(0, len(message), 2) ]
hill_ct = header_pairs + message_pairs

while True:
    K = [
        [rng.randrange(256), rng.randrange(256)],
        [rng.randrange(256), rng.randrange(256)],
    ]
    if ((K[0][0] * K[1][1] - K[0][1] * K[1][0]) & 1) == 1:
        break
B = [rng.randrange(256), rng.randrange(256)]

print("message:")
print(header_pairs)
print(hill_ct)
print(B)
print("CIPHER:")
print(affine_hill_encrypt(hill_ct ,K , B))

cipher_e = [(197, 0), (230, 156), (244, 101), (82, 15), (72, 175), (219, 213), (7, 231), (178, 225)]



def decrypto_s1(cipher):
    header = [(67, 73), (80, 72), (69, 82)]
    dM = [[header[i][0] - header[i+1][0] , header[i][1] - header[i+1][1]]for i in range(2)]
    dC = [[cipher[i][0] - cipher[i+1][0] , cipher[i][1] - cipher[i+1][1]]for i in range(2)]
    print("构造差分矩阵")
    print(dM)
    print(dC)

    rev_dc = revm2(dC)
    print("求解解密矩阵 以行向量形式存储！")
    # ① 主攻击行: 逆乘的顺序反过来, 再转置 —— 出来的直接是解密矩阵 D
    D = transpose(mm2(revm2(dC), dM))      # 你原来: K = mm2(dM, revm2(dC))

    # ② 补仿射项 E (用任意一对已知明文)
    c0, c1 = cipher[0]
    E = [(header[0][0] - (D[0][0]*c0 + D[0][1]*c1)) & 0xFF,
         (header[0][1] - (D[1][0]*c0 + D[1][1]*c1)) & 0xFF]

    # ③ 解密就是一次矩阵乘加 (vm2 可以删了)
    out = [((D[0][0]*c0 + D[0][1]*c1 + E[0]) & 0xFF,
            (D[1][0]*c0 + D[1][1]*c1 + E[1]) & 0xFF) for c0, c1 in cipher]
    print("数据流恢复")
    print(out)
    return out[3:]

hill_ct = [(71, 34), (146, 38), (149, 9), (233, 200), (153, 5), (156, 1), (96, 83), (23, 143), (255, 183), (44, 46), (79, 237), (161, 245), (86, 70), (152, 166), (35, 98), (236, 64), (170, 133), (39, 87), (152, 226), (65, 72), (236, 113), (156, 252), (178, 142), (159, 177), (68, 195), (23, 180), (215, 21), (28, 119), (50, 101), (117, 72), (67, 59), (28, 32), (62, 204), (230, 26), (148, 235), (11, 75), (121, 202), (100, 75), (54, 248)]

decrypto_s1(hill_ct)

#====================[STAGE2]==============================

#!/usr/bin/env python3
"""stage2_demo.py — 演示 Stage 2：双通道二次滤波 LFSR 的"加密"与线性化攻击

流程:
  1. 明文消息 -> 256-bit seed（LFSR 初态，就是要保护的秘密）
  2. 加密: 跑 generate_nostalgia_stream，输出 U/V 两条"密文"流
  3. 攻击: U^V 抵消二次项 -> 掩码回拉 -> GF(2) 高斯消元 -> 恢复 seed/明文

参数与 server.py 完全相同，只是本地独立运行、不经过 Hill 那层。
"""

# ===== 与 server.py 相同的参数 =====
LFSR_TAP = (1 << 10) | (1 << 5) | (1 << 2) | 1   # 反馈多项式 x^256+x^10+x^5+x^2+1
T1_MASK = 0x9E3779B97F4A7C15F39CC0605CEDC8341082276BF3A27251F86C6A11D0C18E95
T2_MASK = 0x6A09E667BB67AE853C6EF372A54FF53A510E527F9B05688C1F83D9AB5BE0CD19
W_MASK  = 0x3C6EF372FE94F82BE73980C0B9DB906821044ED7E744E4A3F0D8D423A1831D2B
REG = (1 << 256) - 1
MASK = T1_MASK ^ T2_MASK ^ W_MASK   # u^v 抵消二次项后剩下的线性掩码


# ================= 加密侧（照搬服务器逻辑）=================
def lfsr_step(state):
    fb = (state & LFSR_TAP).bit_count() & 1       # 抽头位异或得反馈位
    return (state >> 1) | (fb << 255)             # 右移一位，反馈补到最高位

def encrypt(seed, n_bytes=36):
    """双通道二次滤波输出，等价于服务器的 generate_nostalgia_stream"""
    state = seed
    U, V = [], []
    for _ in range(n_bytes):
        u_byte = v_byte = 0
        for _ in range(8):
            w = (state & W_MASK).bit_count()          # 选中位里 1 的个数
            wqf_plus  = ((w * (w + 1)) // 2) & 1      # C(w+1,2) mod 2（二次+线性）
            wqf_minus = ((w * (w - 1)) // 2) & 1      # C(w,  2) mod 2（纯二次）
            u_bit = ((state & T1_MASK).bit_count() & 1) ^ wqf_plus
            v_bit = ((state & T2_MASK).bit_count() & 1) ^ wqf_minus
            u_byte = (u_byte << 1) | u_bit            # 先出的比特在高位
            v_byte = (v_byte << 1) | v_bit
            state = lfsr_step(state)
        U.append(u_byte)
        V.append(v_byte)
    return U, V


# ================= 攻击侧（Stage 2）=================
def gf2_solve(eqs):
    """GF(2) 高斯消元。每个方程 = (系数向量, 右端bit)，用 int 的位表示"""
    basis = {}
    for coeffs, rhs in eqs:
        x = (coeffs << 1) | rhs            # bit0 挂右端，bit1..256 是系数
        while x:
            p = x.bit_length() - 1         # 最高位作为主元
            if p == 0:
                if x & 1:
                    raise ValueError('矛盾方程')
                break
            if p in basis:
                x ^= basis[p]              # 异或消元：GF(2) 的减法就是 XOR
            else:
                basis[p] = x
                break
    sol = 0
    for p in sorted(basis):                # 回代：pivot 是行内最高位，从低位往上解
        row = basis[p]
        if (row & 1) ^ (((row >> 1) & sol).bit_count() & 1):
            sol |= 1 << (p - 1)
    return sol

def attack(U, V):
    """只知道密文 U、V，恢复 256-bit seed"""
    # ① U^V：f+ ^ f- = w^2 ≡ w (mod 2)，二次项全部抵消
    obs = [((u >> b) ^ (v >> b)) & 1 for u, v in zip(U, V) for b in range(7, -1, -1)]
    # ② 每个观测比特 = parity(pb^t(MASK) & seed)，掩码按 LFSR 对偶回拉
    eqs = []
    m = MASK
    for bit in obs:
        eqs.append((m, bit))
        m = ((m << 1) & REG) ^ (LFSR_TAP if (m >> 255) & 1 else 0)  # 必须 XOR
    # ③ 288 个一次方程解 256 个未知数
    seed = gf2_solve(eqs)
    # ④ 验证：用恢复的 seed 重放，应复现全部观测比特
    m = MASK
    for bit in obs:
        assert ((m & seed).bit_count() & 1) == bit
        m = ((m << 1) & REG) ^ (LFSR_TAP if (m >> 255) & 1 else 0)
    return seed


msg = b'YulinSec Stage2 demo!'
assert len(msg) <= 32
seed = int.from_bytes(msg + b'\x00' * (32 - len(msg)), 'big')

U, V = encrypt(seed)
xor_stream = bytes(u ^ v for u, v in zip(U, V))

print('===== 加密侧 =====')
print(f'明文消息   : {msg!r}')
print(f'LFSR seed  : {seed:064x}')
print(f'密文 U (hex): {bytes(U).hex()}')
print(f'密文 V (hex): {bytes(V).hex()}')

print('\n===== 攻击侧 =====')
print(f'U^V 流     : {xor_stream.hex()}  (二次项已抵消，纯线性)')
rec = attack(U, V)
print(f'方程数     : 288，未知数: 256，GF(2) 消元完成')
print(f'恢复 seed  : {rec:064x}')
recovered = rec.to_bytes(32, 'big').rstrip(b'\x00')
print(f'恢复明文   : {recovered!r}')
print(f'\n攻击{"成功" if recovered == msg else "失败"}: seed {"" if rec == seed else "不"}一致')



