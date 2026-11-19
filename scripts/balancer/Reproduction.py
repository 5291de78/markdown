import random as rng

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

cipher = [(197, 0), (230, 156), (244, 101), (82, 15), (72, 175), (219, 213), (7, 231), (178, 225)]

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

#====================[STAGE2]==============================

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




