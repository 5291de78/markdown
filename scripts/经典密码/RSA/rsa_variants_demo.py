# -*- coding: utf-8 -*-
"""
RSA 经典变体学习演示
明文: b"YulinSec{Basic_RSA_1113}"
每个变体一个独立小节，纯标准库实现，只展示核心原理。
注意：演示用 384 位小素数跑得快；真实应用至少 2048 位。
"""


import hashlib, secrets, math

MSG = b"YulinSec{Basic_RSA_1113}"

# ============================================================
# 0. 工具函数：素数生成(Miller-Rabin)、模逆、CRT合并
# ============================================================
def is_prime(n, k=16):
    if n < 2: return False
    for p in (2,3,5,7,11,13,17,19,23,29,31,37):
        if n % p == 0: return n == p
    d, r = n-1, 0
    while d % 2 == 0: d //= 2; r += 1
    for _ in range(k):
        a = secrets.randbelow(n-3) + 2
        x = pow(a, d, n)
        if x in (1, n-1): continue
        for _ in range(r-1):
            x = x*x % n
            if x == n-1: break
        else: return False
    return True

def get_prime(bits):
    while True:
        p = secrets.randbits(bits) | (1 << (bits-1)) | 1
        if is_prime(p): return p

def inv(a, m):
    return pow(a, -1, m)

def crt(mp, mq, p, q):
    """已知 m mod p 和 m mod q，合并出 m mod (p*q)"""
    h = ((mp - mq) * inv(q, p)) % p
    return mq + h * q

def i2b(x):  return x.to_bytes((x.bit_length()+7)//8 or 1, 'big')
def b2i(b):  return int.from_bytes(b, 'big')

BITS = 384          # 演示素数位数
E = 65537

# ============================================================
# 1. 课本 RSA（Textbook RSA）——一切变体的地基
#    c = m^e mod n ;  m = c^d mod n ;  d = e^{-1} mod φ(n)
#    无填充 => 确定性加密 => 不安全（同明文同密文）
# ============================================================
def demo_textbook():
    p, q = get_prime(BITS), get_prime(BITS)
    n, phi = p*q, (p-1)*(q-1)
    d = inv(E, phi)
    c = pow(b2i(MSG), E, n)
    m = pow(c, d, n)
    assert i2b(m) == MSG
    print("[1] Textbook RSA        ok  (m<n 是硬约束)")

# ============================================================
# 2. RSAES-PKCS1-v1_5 —— 在老式 RSA 外套一层填充
#    EM = 0x00 || 0x02 || PS(随机非零字节) || 0x00 || M
#    随机填充 => 同明文每次密文不同；但有 Bleichenbacher 攻击
# ============================================================
def demo_pkcs1_v15():
    p, q = get_prime(BITS), get_prime(BITS)
    n, phi = p*q, (p-1)*(q-1)
    d = inv(E, phi)
    k = (n.bit_length()+7)//8                      # 模数字节数
    ps_len = k - 3 - len(MSG)
    PS = bytes(b for b in secrets.token_bytes(ps_len))  # 简化:PS应非零
    PS = bytes((b or 1) for b in PS)
    EM = b"\x00\x02" + PS + b"\x00" + MSG          # 填充编码
    c = pow(b2i(EM), E, n)
    em = i2b(pow(c, d, n)).rjust(k, b"\x00")
    m = em.split(b"\x00", 2)[2]                    # 去填充
    assert m == MSG
    print("[2] PKCS#1 v1.5 填充    ok  (随机PS => 概率性加密)")

# ============================================================
# 3. RSA-OAEP —— 现代加密标准，CCA 安全
#    用哈希+MGF(掩码生成函数)做两轮 Feistel 式扩散
# ============================================================
def mgf1(seed, length, hlen=32):
    out = b""
    for i in range(-(-length//hlen)):
        out += hashlib.sha256(seed + i.to_bytes(4,'big')).digest()
    return out[:length]

def demo_oaep():
    p, q = get_prime(BITS), get_prime(BITS)
    n, phi = p*q, (p-1)*(q-1)
    d = inv(E, phi)
    k, hlen = (n.bit_length()+7)//8, 32
    lHash = hashlib.sha256(b"").digest()
    # --- 编码 ---
    DB = lHash + b"\x00"*(k-len(MSG)-2*hlen-2) + b"\x01" + MSG
    seed = secrets.token_bytes(hlen)
    maskedDB   = bytes(x^y for x,y in zip(DB, mgf1(seed, k-hlen-1)))
    maskedSeed = bytes(x^y for x,y in zip(seed, mgf1(maskedDB, hlen)))
    EM = b"\x00" + maskedSeed + maskedDB
    c = pow(b2i(EM), E, n)
    # --- 解码 ---
    em = i2b(pow(c, d, n)).rjust(k, b"\x00")
    maskedSeed, maskedDB = em[1:1+hlen], em[1+hlen:]
    seed = bytes(x^y for x,y in zip(maskedSeed, mgf1(maskedDB, hlen)))
    DB   = bytes(x^y for x,y in zip(maskedDB, mgf1(seed, k-hlen-1)))
    assert DB[:hlen] == lHash                        # 校验标签哈希
    m = DB[hlen:].lstrip(b"\x00")[1:]
    assert m == MSG
    print("[3] RSA-OAEP            ok  (哈希扩散 => CCA安全)")

# ============================================================
# 4. Multi-Prime RSA —— n = p*q*r
#    φ(n) = (p-1)(q-1)(r-1)，其余和课本 RSA 一样
#    CTF考点：素数变短 => ECM 分解更容易
# ============================================================
def demo_multiprime():
    p, q, r = get_prime(BITS), get_prime(BITS), get_prime(BITS)
    n, phi = p*q*r, (p-1)*(q-1)*(r-1)
    d = inv(E, phi)
    c = pow(b2i(MSG), E, n)
    assert i2b(pow(c, d, n)) == MSG
    print("[4] Multi-Prime (pqr)   ok  (仅 φ 定义变化)")

# ============================================================
# 5. Takagi RSA —— n = p²q
#    解密技巧：分别对 p 和 q 求根再 CRT 合并
#    dp = e^{-1} mod (p-1),  dq = e^{-1} mod (q-1)
# ============================================================
def demo_takagi():
    p, q = get_prime(BITS), get_prime(BITS)
    n = p*p*q
    c = pow(b2i(MSG), E, n)
    dp, dq = inv(E, p-1), inv(E, q-1)
    m = crt(pow(c, dp, p), pow(c, dq, q), p, q)
    assert i2b(m) == MSG
    print("[5] Takagi (p²q)        ok  (mod p 与 mod q 分别求根)")

# ============================================================
# 6. RSA-CRT —— 私钥拆成 (dp, dq, qinv) 加速解密
#    速度约快4倍；⚠️ 故障攻击(DFA)的主要目标
# ============================================================
def demo_rsa_crt():
    p, q = get_prime(BITS), get_prime(BITS)
    n, phi = p*q, (p-1)*(q-1)
    d = inv(E, phi)
    dp, dq, qinv = d % (p-1), d % (q-1), inv(q, p)   # 私钥三件套
    c = pow(b2i(MSG), E, n)
    m = crt(pow(c, dp, p), pow(c, dq, q), p, q)
    assert i2b(m) == MSG
    print("[6] RSA-CRT 加速        ok  (一半位宽的两次模幂+合并)")

# ============================================================
# 7. Rabin 密码 —— c = m² mod n（e=2 的"RSA"）
#    破译难度 ⟺ 分解 n（有严格证明，RSA 没有）
#    解密得 4 个根 => 需要冗余标记挑出正确明文
#    要求 p ≡ q ≡ 3 (mod 4) 以便直接开方
# ============================================================
def demo_rabin():
    def prime3mod4():
        while True:
            p = get_prime(BITS)
            if p % 4 == 3: return p
    p, q = prime3mod4(), prime3mod4()
    n = p*q
    marker = b"::YK"                                # 冗余标记
    m = b2i(MSG + marker)
    c = pow(m, 2, n)
    mp, mq = pow(c, (p+1)//4, p), pow(c, (q+1)//4, q)
    roots = [crt(a, b, p, q) for a in (mp, p-mp) for b in (mq, q-mq)]
    found = [i2b(r) for r in roots if i2b(r).endswith(marker)]
    assert found and found[0][:-4] == MSG
    print(f"[7] Rabin (c=m²)        ok  (4个根中靠标记选中明文)")

# ============================================================
# 8. RSA 盲签名 —— 签名者看不到内容
#    盲化 m' = m·r^e ; 签名 s' = m'^d ; 去盲 s = s'·r^{-1} = m^d
#    依据：RSA 的乘法同态性
# ============================================================
def demo_blind_sig():
    p, q = get_prime(BITS), get_prime(BITS)
    n, phi = p*q, (p-1)*(q-1)
    d = inv(E, phi)
    m = b2i(MSG)
    while True:                                     # r 必须与 n 互素
        r = secrets.randbelow(n-2) + 2
        if math.gcd(r, n) == 1: break
    m_blind = m * pow(r, E, n) % n                  # 用户盲化
    s_blind = pow(m_blind, d, n)                    # 签名者盲签(看不到m)
    s = s_blind * inv(r, n) % n                     # 用户去盲
    assert pow(s, E, n) == m                        # 公开验证 s^e == m
    print("[8] RSA 盲签名          ok  (乘法同态 => 签完不知内容)")

# ============================================================
# 9. RSA-PSS 签名(简化版) —— 带随机盐的概率签名
#    EM = Hash(m || salt) || salt ;  s = EM^d mod n
#    盐让同一消息每次签名不同，抗伪造（真实PSS还有MGF掩码层）
# ============================================================
def demo_pss_sig():
    p, q = get_prime(BITS), get_prime(BITS)
    n, phi = p*q, (p-1)*(q-1)
    d = inv(E, phi)
    salt = secrets.token_bytes(16)
    h = hashlib.sha256(MSG + salt).digest()
    em = b2i(h + salt)                              # 简化编码(真PSS更长)
    s = pow(em, d, n)
    em2 = pow(s, E, n)                              # 验证:恢复 EM
    h2, salt2 = i2b(em2)[:32], i2b(em2)[32:]
    assert h2 == hashlib.sha256(MSG + salt2).digest()
    print("[9] RSA-PSS 签名(简化)  ok  (随机盐 => 概率性签名)")

if __name__ == "__main__":
    print(f"明文: {MSG.decode()}\n" + "-"*48)
    demo_textbook()
    demo_pkcs1_v15()
    demo_oaep()
    demo_multiprime()
    demo_takagi()
    demo_rsa_crt()
    demo_rabin()
    demo_blind_sig()
    demo_pss_sig()
    print("-"*48 + "\n全部变体加解密/签验通过 ✔")
