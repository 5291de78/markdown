

[RSA公因数攻击（多组nc） | 知了 – 朝闻道，夕可眠矣。](https://zhile.in/blog/CTF/CRYPTO/RSA-common-factor-multi-n-c)

- 共模：相同 N、相同 m、不同 e，gcd (e1,e2)=1 → 直接求 m，不用分解 N
- 共享素数攻击：n1,n2 不同，gcd (n1,n2)=p → 直接拿到 p，分解 N
- Wiener：d 很小，e 已知，求 d
- 低指数广播（Håstad）：同一个 m，多个不同 N、不同 e，e 很小，CRT 恢复 m

# GCD攻击



# 共模攻击

## 原理推导

由扩展欧几里得（贝祖定理），因为 $\gcd(e_1,e_2)=1$，一定存在整数 $(s,t)$，使得：

$$e_1\cdot s + e_2\cdot t = 1$$

$(s,t)$ 一定一正一负。

$$c_1^s \cdot c_2^t \equiv (m^{e_1})^s \cdot (m^{e_2})^t \equiv m^{e_1 s + e_2 t} \equiv m^{1} \equiv m \pmod N$$
