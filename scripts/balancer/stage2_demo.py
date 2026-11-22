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


def main():
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


if __name__ == '__main__':
    main()
