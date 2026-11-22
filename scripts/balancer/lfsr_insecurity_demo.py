# -*- coding: utf-8 -*-
"""
Demonstrate the insecurity of LFSR-based stream encryption and reproduce the
core idea of the paper behind the "Nostalgia" design (ePrint 2025/2140):
weightwise-quadratic filtered LFSR -- and how the two-channel leak in the
challenge cancels the quadratic part, leaving a GF(2) linear system.
"""
import random as rng

TAP = (1 << 10) | (1 << 5) | (1 << 2) | 1          # x^256 + x^10 + x^5 + x^2 + 1
T1 = 0x9E3779B97F4A7C15F39CC0605CEDC8341082276BF3A27251F86C6A11D0C18E95
T2 = 0x6A09E667BB67AE853C6EF372A54FF53A510E527F9B05688C1F83D9AB5BE0CD19
W = 0x3C6EF372FE94F82BE73980C0B9DB906821044ED7E744E4A3F0D8D423A1831D2B
MASK = (1 << 256) - 1


def lfsr_step(state):
    fb = (state & TAP).bit_count() & 1
    return (state >> 1) | (fb << 255)


def dual_step(C):
    """lfsr_step 的对偶: parity(lfsr_step(x) & C) == parity(x & dual_step(C))"""
    top = (C >> 255) & 1
    C = (C << 1) & MASK
    if top:
        C ^= TAP
    return C


def nostalgia_stream(seed, n_bytes):
    """挑战原版的 (U,V) 双通道流"""
    state = seed
    U, V = [], []
    for _ in range(n_bytes):
        ub = vb = 0
        for _ in range(8):
            w = (state & W).bit_count()
            wp = (w * (w + 1) // 2) & 1          # weightwise quadratic (plus)
            wm = (w * (w - 1) // 2) & 1          # weightwise quadratic (minus)
            u = ((state & T1).bit_count() & 1) ^ wp
            v = ((state & T2).bit_count() & 1) ^ wm
            ub = (ub << 1) | u
            vb = (vb << 1) | v
            state = lfsr_step(state)
        U.append(ub)
        V.append(vb)
    return U, V


def gf2_solve(eqs, nvar):
    """eqs: [(coeff_int, rhs_bit)], coeff 为 nvar 位整数。满秩返回唯一解, 否则 None。"""
    basis = {}
    CM = (1 << nvar) - 1
    for coeff, rhs in eqs:
        x = coeff | (rhs << nvar)
        while True:
            cx = x & CM                       # 只看系数位, rhs 位(第 nvar 位)不参与消元
            if cx == 0:
                if (x >> nvar) & 1:           # 0 = 1, 矛盾
                    return None
                break                         # 0 = 0, 冗余方程
            i = cx.bit_length() - 1
            if i in basis:
                x ^= basis[i]
            else:
                for j in basis:                # 先消掉 x 里其它主元列(保持 RREF 不变量)
                    if (x >> j) & 1:
                        x ^= basis[j]
                for j, r in list(basis.items()):   # 新主元消进所有旧行
                    if (r >> i) & 1:
                        basis[j] = r ^ x
                basis[i] = x
                break
    if len(basis) < nvar:
        return None
    seed = 0
    for i, r in basis.items():
        if (r >> nvar) & 1:
            seed |= 1 << i
    return seed


def parity(x):
    return x.bit_count() & 1


# ----------  sanity checks ----------
assert all((((w * (w + 1) // 2) & 1) ^ ((w * (w - 1) // 2) & 1)) == (w & 1) for w in range(600)), "quadratic cancellation identity"
for _ in range(50):  # dual_step 正确性: 与 256 个基向量演化对比
    x = rng.getrandbits(256)
    C = rng.getrandbits(256)
    assert parity(lfsr_step(x) & C) == parity(x & dual_step(C))
print("[sanity] w(w+1)/2 ⊕ w(w-1)/2 = w (mod 2)  ✓")
print("[sanity] dual_step 与正向演化一致  ✓")

# ---------- Part A: 裸 LFSR(无滤波) ----------
print("\n===== Part A: 裸 LFSR 输出直接线性可解 =====")
seed = rng.getrandbits(256)
st, C, eqs = seed, 1, []
for t in range(256):
    eqs.append((C, st & 1))            # 观测 state 的最低位, 系数掩码随对偶 LFSR 演化
    C = dual_step(C)
    st = lfsr_step(st)
rec = gf2_solve(eqs, 256)
print(f"观测 256 bit LSB 流 → 恢复 seed: {rec == seed}")

# ---------- Part B: weightwise 二次滤波 + 双通道抵消 ----------
print("\n===== Part B: Nostalgia 双通道流的 u⊕v 线性化攻击 =====")
def attack(U, V, nvar=256):
    C = T1 ^ T2 ^ W
    eqs = []
    for ub, vb in zip(U, V):
        for k in range(8):
            s = ((ub >> (7 - k)) & 1) ^ ((vb >> (7 - k)) & 1)   # u_t ⊕ v_t
            eqs.append((C, s))
            C = dual_step(C)
    return gf2_solve(eqs, nvar)

ok, bits_needed = 0, []
for _ in range(20):
    seed = rng.getrandbits(256)
    U, V = nostalgia_stream(seed, 36)      # 服务端就给 36 字节
    C = T1 ^ T2 ^ W
    eqs = []
    rec = None
    for idx, (ub, vb) in enumerate(zip(U, V)):
        for k in range(8):
            eqs.append((C, ((ub >> (7 - k)) & 1) ^ ((vb >> (7 - k)) & 1)))
            C = dual_step(C)
            r = gf2_solve(eqs, 256) if len(eqs) >= 256 else None
            if r is not None:
                rec, need = r, len(eqs)
                break
        if rec is not None:
            break
    assert rec == seed
    ok += 1
    bits_needed.append(need)
print(f"20/20 实例: 36 字节 (U,V) 流全部恢复 256-bit seed ✓")
print(f"所需观测 bit 数: min={min(bits_needed)}, max={max(bits_needed)} (理论下界 256)")
