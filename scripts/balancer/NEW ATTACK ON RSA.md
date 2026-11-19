# NEW ATTACK ON RSA

读完了（Jiménez Urroz, *A New Attack to RSA with Small Private Exponent and Partial Information*，15 页）。这篇就是怀旧之秤 Stage 3 注释里引的 ePrint 2026/1295。它的核心思想一句话：**Wiener 连分数攻击换个"更准的分母"，把已知的 p+q 高位信息直接折算成对私钥指数界的提升**。下面按论文结构讲。

## 一、先回顾它要改进什么：经典 Wiener 的瓶颈

RSA 恒等式：`ed − kφ(n) = 1`，其中 `φ(n) = n + 1 − (p+q)`。Wiener 的做法是对 `e/n` 做连分数展开：

$$\frac{e}{n} = \frac{k}{d}\left(1 - \frac{p+q-1-\tfrac1k}{n}\right)$$

括号里的误差项 ~ `(p+q)/n ~ N^{1/2}/N = N^{-1/2}`。由 Legendre 定理（`|α − k/d| < 1/(2d²)` ⇒ `k/d` 是 α 的收敛分），要求 `N^{-1/2} < 1/(2d²)`，即 **d < N^{1/4}**。

**瓶颈就在这个误差项**：它大，是因为我们不知道 p+q，只能用 n 硬凑出 φ(n) 的粗糙近似。

## 二、论文的核心 trick：把分母从 n 换成 n − x

假设我们知道 p+q 的一部分：写成

$$p + q - 1 = x + R,\quad x\ \text{已知（高位）},\ R\ \text{未知小余项}$$

那么 `φ(n) = n − x − R`，代回恒等式并两边除以 `d(n−x)`：

$$\frac{e}{n-x} = \frac{k}{d}\left(1 - \frac{R}{n-x}\right) + \frac{1}{d(n-x)}$$

**误差项从 `~N^{-1/2}` 缩到了 `~R/N`**。R 越小（p+q 知道得越多），`e/(n-x)` 就越接近 `k/d`，连分数就能在 d 大得多的情况下仍把 `k/d` 捞成收敛分。这就是摘要里"very simple modification"的全部内容——**不改方法，改分母**。

## 三、界是怎么算出来的（Theorem 3.1 + 主定理）

论文用 Wiener 引理（Lemma 2.5）给出收敛条件，推出关键不等式：

$$kd < \frac{2}{3}\cdot\frac{n-x}{R - \tfrac1k} \quad\Longrightarrow\quad d < \sqrt{\frac{2n}{3eR}}\ \ (\text{当 } e\sim n)$$

然后把"知道 p+q 的高位"量化：定义 **δ-近似** `p+q = K + U, |U| < c·(p+q)^{1−δ}`（Section 4），并证明（Lemma 4.2）**δ-近似等价于知道 p+q 的 δ 比例的最高有效位（MSBs）**——就是你手里"top 256 bits"那种信息。代入得主定理：

$$\boxed{\ |p+q - S| < n^{(1-\delta)/2} \ \Longrightarrow\ \text{可解出 } d \text{ 只要 } d < n^{\frac{1+\delta}{4}}\ }$$

**这个界的物理意义**（论文卖点）：

| 已知 p+q 的 MSB 比例 δ | 私钥界                  | 对比                               |
| ---------------------- | ----------------------- | ---------------------------------- |
| 0（一无所知）          | n^{1/4}                 | 退回经典 Wiener                    |
| 1/2                    | **n^{3/8} ≈ n^{0.375}** | **超过 Boneh-Durfee 的 n^{0.292}** |
| 1（全部知道）          | n^{1/2}                 | 相当于 φ 已知，平凡                |

超过 Boneh-Durfee 不说，它还**无条件**——Boneh-Durfee 系的 Coppersmith 格方法都依赖"格规约给出的解代数独立"这个从未被证明的假设，连分数方法没有（论文第 4 段特意强调这一点）。

## 四、算法本身（Section 3 的 Algorithm，朴素得可爱）

```
输入: e, n, x          # x = 已知的 p+q−1 高位部分
1. 对 e/(n−x) 做连分数展开, 枚举收敛分 (ni, di)
2. 对每个 di:  L = (e·di − 1) / ni        # 候选 φ(n)
3. 解 X² − (n − L + 1)X + n = 0
4. 若两根为自然数且乘积为 n → 输出 (di, p, q)
```

复杂度 O(log e)，多项式时间。收敛分必中是因为 Theorem 3.1 保证了 `k/d` 一定出现在收敛分里，而 `(ni, di) = 1` 和 `(k, d) = 1`（式 (1)(4)）让你能直接读出 `k = ni, d = di`。

论文还附带一个暴力增强（Remark 3.2）：如果模数不太大，可以枚举猜测 x（每次试 O(√n/2^l) 次），512 位模数猜 200 位的情况下只需重试 256 次就能在零信息下打到 d < n^{0.3}——对你这题用不上，但思路是一脉相承的"用计算换信息"。

## 五、映射到你的怀旧之秤 Stage 3

题目参数：广义 RSA `e·u ≡ 1 (mod Ψ)`，`Ψ = (p−a)(q−a)`（a=7），`u ≈ N^{0.332}`，且泄露 **S = p+q 的高 256 位**（shift_bits 直接给了）。攻击就是把论文方法平移到 Ψ 上：

1. **构造修正分母**：`Ψ = N − a·S + a² = (N − a·S̃ + a²) − a·r`，其中 `S̃ = seed << shift_bits`（Stage 2 解 LFSR 出来的），`r = S − S̃` 是未知的低位余项；
2. **跑修正连分数**：对 `e/Ψ̃`（`Ψ̃ = N − a·S̃ + a²`）做 CF，误差项 = `a·r/Ψ̃`；
3. **验证可行性**：`r < 2^{257}` ⇒ `R = a·r ≈ 2^{260}`，`u = 2^{340}`，界 `u < √(2N/(3R)) ≈ (2^{1024}/2^{260})^{1/2} = 2^{382} = N^{0.373}`——**u = N^{0.332} < N^{0.373}，正好落在攻击窗口内**（这就是为什么题目敢用 0.332 > 0.292 的 u：Boneh-Durfee 打不动，但 p+q 高位把连分数抬过了它）；
4. **回收因子**：收敛分给出 `u`（和 k）→ `Ψ = (e·u − 1)/k` → `S = (N + a² − Ψ)/a` → 解 `Y² − (S − 2a)Y + Ψ = 0` 得 `p−a, q−a` → **p, q**；
5. **拿 flag**：p, q 已知后走标准 RSA：`φ(N) = (p−1)(q−1)`（keygen 保证 gcd(e, φ(N))=1），`d' = e⁻¹ mod φ(N)`，`m = c_rsa^{d'} mod N` → long_to_bytes 出 flag。

论文在 `markdown/cryptom/文献/A NEW ATTACK TO RSA WITH SMALL PRIVATE.pdf`，精读时重点看 Section 3 定理证明（误差放缩那几步）和 Section 5 的实验——他 512 位模数 + d < n^0.3 的实验正好对应你题目的量级。