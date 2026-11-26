# Coppersmith Method（Coppersmith 方法）

Don Coppersmith 在1996年提出的**基于格基规约（LLL）**的密码分析工具：**求解模多项式方程的小整数根**，是CTF、RSA密码分析里最核心的格攻击手段之一。

> 一句话：给定 $F(x)\equiv 0 \pmod N$，在根 $x_0$ 足够小的时候，可以用 LLL 把这个模方程变成**整数域上的多项式方程**，直接求根。

## 1. 一元定理（最常用）

设 $F(x)\in\mathbb Z[x]$，次数 $d$，模数 $N$（不一定是素数），若存在整数根 $x_0$ 满足 $$F(x_0)\equiv 0 \pmod N,\quad |x_0|<N^{1/d}$$ 则 Coppersmith 方法可以在多项式时间内找到 $x_0$。

> 例：$F(x)=x^3-C$，$(d=3)$，只要 $|x_0|<N^{1/3}$ 就能解；这就是小e=3 RSA经典攻击。

## 2. 核心思路（三步走）

1. **构造辅助多项式**：构造一族多项式 $F_k(x)=x^i N^j F(x)^k$，它们都满足 $F_k(x_0)\equiv 0 \pmod{N^k}$；
2. **拼成格**：把这些多项式的系数作为格向量，得到一个格；
3. **LLL规约**：LLL 输出一个很短的向量，对应一个**系数很小的多项式 $(G(x))$**。 因为系数足够小，$G(x_0)\equiv0 \pmod{N^k}$ 直接推出 $G(x_0)=0$（整数等式），然后用有理根定理/求根得到 $x_0$。

本质：**把模根问题 → 格短向量问题 → 整数多项式求根**。

## 3. 二元/多元推广

Coppersmith 也给出二元版本：$(F(x,y)=0)$，在解 $(x_0,y_0)$ 有界时，启发式用格找小根。 经典场景：

- 已知 $p$ 的高位比特，分解 $(N=pq)$（Coppersmith 已知高位分解）
- Boneh–Durfee 攻击：RSA 私钥 $d<N^{0.292}$，二元 Coppersmith 变体，是 Wiener 攻击的增强版

## 4. 密码学 / CTF 典型应用

1. **小公钥e RSA（e=3）**：明文很小、或明文有固定前缀，Håstad广播攻击（多用户同明文加密）；
2. **部分已知p/q**：拿到素因子一部分比特，恢复完整 $(p,q)$；
3. **短填充RSA（short pad）**；
4. Boneh-Durfee：小私钥d攻击；
5. 很多SageMath密码题里的 `coppersmith` 函数底层就是这套。

## 5. 重要局限

- 只对**小根**有效；根超过界 $N^{1/d}$ 理论上不保证成功；
- 多元版本**没有严格定理，是启发式**，高维格LLL很慢；
- 格维度越高，LLL开销爆炸，实战一般只适合低次数、低维场景。

## 6. 和LLL的关系

LLL是底层格规约算法；Coppersmith是**一套构造格、选辅助多项式的框架**，LLL是它的子模块。

> 很多CTF选手说“Coppersmith攻击”，就是指这套LLL格求解小根的套路。

------

如果你需要，我可以给你：

- SageMath 一元 Coppersmith 可直接跑模板；
- 或者严格的数学证明版本；
- 或者一道经典 e=3 RSA Coppersmith例题。

# 中国剩余定理（CRT，Chinese Remainder Theorem）

## 一、基础版本（模数两两互素）

设有同余方程组： $$ \begin{cases} x \equiv a_1 \pmod{m_1}\ x \equiv a_2 \pmod{m_2}\ \quad\vdots\ x \equiv a_k \pmod{m_k} \end{cases} $$ 如果 $m_1,m_2,\dots,m_k$ **两两互质**，则：

1. 在模 $M=m_1m_2\cdots m_k$ 下，**存在唯一解**；
2. 通解形式：$x = x_0 + tM,\ t\in\mathbb Z$，$x_0$ 是一个特解。

### 求解公式

令 $M = \prod m_i,\ M_i = \dfrac{M}{m_i}$ 求 $M_i$ 在模 $m_i$ 下的逆元 $M_i^{-1}$，即 $M_i\cdot M_i^{-1}\equiv 1\pmod{m_i}$ $$ \boldsymbol{x_0 = \sum_{i=1}^k a_i M_i M_i^{-1} \pmod{M}} $$

✅ 例子： $$ \begin{cases} x\equiv 2 \pmod 3\ x\equiv 3 \pmod 5\ x\equiv 2 \pmod 7 \end{cases} $$ $M=3\cdot5\cdot7=105$ $M_1=35,\ M_2=21,\ M_3=15$ $35^{-1}\equiv 2\pmod3,\ 21^{-1}\equiv 1\pmod5,\ 15^{-1}\equiv 1\pmod7$ $$ x_0 = 2\cdot 35\cdot 2 + 3\cdot 21\cdot 1 + 2\cdot 15\cdot 1 = 233 \equiv 23 \pmod{105} $$ 解：$x\equiv 23 \pmod{105}$

------

## 二、一般版本（模数不一定互素，扩展CRT）

模数不互质时，**不一定有解**。 思路：两两合并同余式，逐步化简。 $$ \begin{cases} x\equiv a_1 \pmod{m_1}\ x\equiv a_2 \pmod{m_2} \end{cases} $$ 写成：$x = a_1 + k m_1$ 代入第二个式子： $$ a_1 + k m_1 \equiv a_2 \pmod{m_2} \implies m_1 k \equiv (a_2-a_1) \pmod{m_2} $$ 这是关于 $k$ 的一元一次同余方程。 设 $d=\gcd(m_1,m_2)$

- 如果 $d \nmid (a_2-a_1)$：**无解**
- 如果 $d \mid (a_2-a_1)$：有解，合并为新同余式 $$ x \equiv a_{\text{new}} \pmod{\text{lcm}(m_1,m_2)} $$ 不断合并直到只剩一个式子。

> 扩展CRT是CTF密码题里更常用的！

------

## 三、密码学里的作用（RSA/Coppersmith 相关）

1. **RSA-CRT加速解密** $(N=pq)$，$(p,q)$ 素数。 $$ \begin{cases} m \equiv c^{d_p} \pmod p,\quad d_p = d \bmod (p-1)\ m \equiv c^{d_q} \pmod q,\quad d_q = d \bmod (q-1) \end{cases} $$ 用CRT合并得到 $m$，速度远快于直接算 $c^d \bmod N$。 👉 同时也是**CRT故障攻击（Bellcore攻击）**的基础：注入故障，拿到一个错误分支，直接分解N。
2. 和Coppersmith配合： 很多RSA题目先用CRT把多个同余条件拼起来，再上Coppersmith求小根。
3. Hastad广播攻击本质： 多个用户，相同明文 $m$，不同 $N_i$，加密 $c_i\equiv m^e \pmod{N_i}$。 模数两两互素时CRT恢复 $m^e$，再开e次方得到 $m$。

------

## 四、Sage 极简模板

```
# 普通CRT（模数互素）
crt([3,5,7], [2,3,2])
# 返回 (23, 105) 代表解23 mod 105

# 扩展CRT（模数不互素也能算）
from sage.modules.free_module_integer import IntegerLattice
# 或者用内置 crt 新版本自动处理可合并情况
```

## 五、易错点总结

- 基础CRT前提：模数两两互素，才有模M唯一解；
- 模数不互素一定要用**扩展CRT**，先判是否有解；
- CRT得到的是**同余类**，不是单个数字；
- CRT是**构造性证明**，直接给求解算法。

如果你想要，我可以给：

- 扩展CRT完整推导 + Python手写代码（不依赖sage）
- 或者 Hastad广播攻击的例题（CRT+开方）

# Side-Channel Attacks（SCA，侧信道攻击 / 旁路攻击）

一句话核心：**不攻击密码算法本身的数学弱点，而是利用密码实现运行时无意泄露的物理/软件旁路信息，恢复密钥**。

> 哪怕AES、RSA在数学上安全，只要硬件/软件实现会泄露旁路信号，就可以被攻破。 和你前面学的 CRT、Coppersmith 对比：
>
> - CRT / Coppersmith：**代数密码分析**，盯着方程、模、格；
> - SCA：**实现层面攻击**，盯着芯片跑的时候漏出来的额外信号。

分为两大类：**被动侧信道（只观测）**、**主动故障注入（主动干扰设备）**

## 一、被动侧信道（Passive SCA）

攻击者不干扰设备，只是采集泄露信号

1. **Timing Attack 时序攻击（Kocher 1996）** 原理：不同密钥分支、不同中间值，执行耗时不一样。 典型：RSA 平方乘（square-and-multiply），私钥比特是1就多一次乘法，时间更长；测量解密耗时，逐位读出私钥。 软件里常见：密码比较逐字节return，不同长度的比对时间差；Cache攻击（Spectre/Meltdown）也属于时序类微架构侧信道。
2. **Power Analysis 功耗分析（最经典，CTF硬件题高频）** 芯片晶体管翻转数量决定瞬时电流，功耗和处理数据的**汉明重量 / 汉明距离**强相关。

- SPA Simple Power Analysis 简单功耗分析：直接看单条功耗曲线，肉眼区分乘、平方，读出RSA私钥bit；
- DPA Differential Power Analysis 差分功耗分析：多组轨迹+统计，区分0/1；
- CPA Correlation Power Analysis 相关功耗分析：计算假设功耗模型和真实轨迹的相关系数，现在最常用（AES S盒攻击标配）

1. **EM Analysis 电磁分析** 芯片运行向外辐射电磁波，用近场天线采集，和功耗分析模型几乎一样；优势：**非侵入、可以定位芯片局部模块**，不用拆封装、不用接电源探头。
2. 其他小众被动信道：声学（听风扇/电容声音）、光泄露、总线信号。

## 二、主动侧信道：Fault Injection（故障攻击，DFA）

主动给芯片制造异常，让它算出错误结果，再用错误输出代数反推密钥。

> 你前面学的 **CRT故障攻击（Bellcore攻击）** 就是它最经典例子！ RSA用CRT解密，给p分支注入故障，拿到错误密文，$\gcd(\text{err}-c,N)=p$，直接分解N。

注入手段：电压毛刺、时钟毛刺、激光、EM脉冲、温度扰动。 DFA（Differential Fault Analysis）：AES故障攻击，只需要1个错误密文，就能恢复AES密钥。

## 三、密码学里的典型目标

- RSA：SPA、时序、CRT故障攻击；
- AES：CPA、DPA、DFA；
- ECC：功耗/时序攻击，恢复私钥；
- 智能卡、安全芯片、FPGA、MCU是重灾区。

## 四、防护思路（Countermeasures）

1. 时序：**恒定时间实现（constant-time）**，消除分支和操作的数据相关延迟；随机抖动时间；
2. 功耗：掩码（masking，把密钥拆成多份共享）、乱序执行、随机化运算顺序；
3. 硬件：金属屏蔽、滤波电源、检测故障；
4. 算法层：避免带分支的平方乘，用固定窗口、蒙哥马利固定时间乘法。

## 五、和你之前知识点串联（非常重要）

- CRT：RSA-CRT加速解密 → 同时引入Bellcore故障攻击（SCA的一种）；
- Coppersmith：代数求解小根；SCA拿到泄露/错误值之后，经常配合Coppersmith、CRT一起做代数恢复密钥；
- 很多CTF硬件crypto题流程：采集trace做CPA得到部分密钥字节 / 注入故障得到错误输出 → 再上CRT/Coppersmith补全剩余密钥。

## 六、术语小结

- SCA：Side Channel Analysis 侧信道分析
- SPA：Simple Power Analysis
- DPA：Differential Power Analysis
- CPA：Correlation Power Analysis
- DFA：Differential Fault Analysis
- Timing attack：时序攻击
- FI：Fault Injection 故障注入

要不要我给你写一个极简CPA攻击AES的原理+Python模拟（汉明重量模型）？





![1795046164906](C:\Users\wangq\Desktop\markdown\计算机科学\mind_pic\1795046164906.png)

![1795046178025](C:\Users\wangq\Desktop\markdown\计算机科学\mind_pic\1795046178025.png)

这段内容构造的是**有限简单连分数的渐近分数（convergents）递推体系**，是连分数数论的核心基础公式，也是你正在读的 RSA 小私钥 d 攻击（Wiener 攻击）的数学根基。

下面逐部分拆解：

------

### 一、符号前提

$\langle q_0, q_1, \dots, q_i \rangle$ 是**有限简单连分数**的简写，展开形式为： $$ \langle q_0, q_1, \dots, q_i \rangle = q_0 + \cfrac{1}{q_1 + \cfrac{1}{\ddots + \cfrac{1}{q_i}}} $$ 其中 $q_i$ 称为**部分商（partial quotient）**，对应欧几里得算法每一步的整数商；$\dfrac{n_i}{d_i}$ 称为这个连分数的第 $i$ 个**渐近分数**。

------

### 二、公式 (2)：渐近分数的递推构造

这组式子是全文的核心构造：**从部分商 $q_i$ 出发，线性递推计算每一级渐近分数的分子 $n_i$ 和分母 $d_i$**。

- 初始条件： $$ n_0 = q_0,\quad d_0 = 1 $$ $$ n_1 = q_0 q_1 + 1,\quad d_1 = q_1 $$
- 递推关系（对任意 $2\le i\le m$）： $$ \begin{cases} n_i = q_i \cdot n_{i-1} + n_{i-2}\[4pt] d_i = q_i \cdot d_{i-1} + d_{i-2} \end{cases} $$

它的意义是：不用一层层嵌套展开连分数，只要拿到所有部分商，就可以用线性递推高效算出每一级的分子、分母。

------

### 三、公式 (3)：连分数核心恒等式

$$ n_i d_{i-1} - d_i n_{i-1} = (-1)^{i+1} $$ 这是连分数最重要的行列式恒等式：相邻两个渐近分数的“叉乘差”绝对值恒为 1，符号交替。

它直接推出公式 (4)： $$ \gcd(n_i,, d_i) = 1 $$ 即**每一个渐近分数都是既约分数**，分子分母天然互素。

> 这一点对 Wiener 攻击至关重要：我们对 $(e/N)$ 做连分数展开得到候选分数 $n_i/d_i$，因为它天然互素，所以可以直接把 $n_i$ 当 $k$、$d_i$ 当私钥候选，无需额外约分验证。

------

### 四、Remark 2.2 的含义

注意最后一个部分商满足 $q_m \ge 2$；否则会推出欧几里得算法中倒数第二个余数 $r_{m-1}=1$，这在规范的连分数展开中不成立。

> 背景：有限连分数有两种写法（最后一项是1，或者把1合并到前一项），标准约定最后一个部分商必须 ≥2，保证展开唯一。

------

### 五、和 RSA 攻击的对应关系

你前面读到的“连分数攻击 RSA 小私钥 d”，完整逻辑就建立在这套构造上：

1. 由 RSA 密钥关系 $ed - k\varphi(N)=1$，可推导出 $\dfrac{k}{d}$ 是 $\dfrac{e}{N}$ 的一个极近有理逼近；
2. 连分数的渐近分数是**最佳有理逼近**：任何足够近的有理数，一定是目标数连分数展开的某个渐近分数；
3. 对 $(e/N)$ 做连分数展开，用上面的递推式算出所有渐近分数 $n_i/d_i$；
4. 逐个验证 $d_i$ 是否为合法私钥，即可恢复小私钥 $d$。

需要我给一个完整的 Wiener 攻击手算小例子，用这套递推式一步步算出私钥 d 吗？

## 一、具体怎么用：一步一步手算示例

我们拿分数 $\boldsymbol{\dfrac{41}{16}}$ 完整走一遍流程，完全对应你原文里的公式。

### 步骤1：求连分数的部分商 $q_i$

用**欧几里得辗转相除法**，每一步的整数商就是部分商 $q_i$： $$ \begin{align*} 41 &= 2\cdot 16 + 9 \implies q_0=2\ 16 &= 1\cdot 9 + 7 \implies q_1=1\ 9 &= 1\cdot 7 + 2 \implies q_2=1\ 7 &= 3\cdot 2 + 1 \implies q_3=3\ 2 &= 2\cdot 1 + 0 \implies q_4=2 \end{align*} $$ 因此该分数的连分数记作：$\dfrac{41}{16} = \langle 2,1,1,3,2 \rangle$

### 步骤2：用递推公式计算渐近分数

按原文公式(2)，逐级计算每个渐近分数的分子 $n_i$、分母 $d_i$：

- 初始项： $(i=0)$：$n_0=q_0=2,\quad d_0=1$ → 第0个渐近分数：$\dfrac{2}{1}$ $(i=1)$：$n_1=q_0q_1+1=2\cdot1+1=3,\quad d_1=q_1=1$ → 第1个渐近分数：$\dfrac{3}{1}$
- 递推项（$i\ge2$）：$n_i = q_i n_{i-1} + n_{i-2},\quad d_i = q_i d_{i-1} + d_{i-2}$ $(i=2)$：$n_2=1\cdot3+2=5,\quad d_2=1\cdot1+1=2$ → $\dfrac{5}{2}$ $(i=3)$：$n_3=3\cdot5+3=18,\quad d_3=3\cdot2+1=7$ → $\dfrac{18}{7}$ $(i=4)$：$n_4=2\cdot18+5=41,\quad d_4=2\cdot7+2=16$ → $\dfrac{41}{16}$

最后一级恰好等于原分数，计算正确。

### 步骤3：验证核心恒等式(3)

$$n_i d_{i-1} - d_i n_{i-1} = (-1)^{i+1}$$

- $(i=1)$：$3\cdot1 - 1\cdot2 = 1 = (-1)^{2}$ ✔️
- $(i=2)$：$5\cdot1 - 2\cdot3 = -1 = (-1)^{3}$ ✔️
- $(i=3)$：$18\cdot2 - 7\cdot5 = 1 = (-1)^{4}$ ✔️
- $(i=4)$：$41\cdot7 - 16\cdot18 = -1 = (-1)^{5}$ ✔️

### 在 RSA 攻击中的实际用法

对 RSA 的公钥比值 $(e/N)$ 做上述连分数展开，得到所有渐近分数的分母 $d_i$； 由于小私钥 $d$ 满足 $\dfrac{k}{d}$ 是 $\dfrac{e}{N}$ 的最佳有理逼近，它必然是某一级渐近分数。因此**遍历所有 $d_i$，验证其能否正确解密密文**，即可快速找到真实私钥 $d$（Wiener 攻击的核心逻辑）。

------

## 二、简单证明

### 1. 递推公式(2)的证明

采用**数学归纳法**，核心利用连分数的基本性质：

> 第 $i$ 级连分数，等价于把第 $i-1$ 级连分数的最后一个部分商 $q_{i-1}$ 替换为 $q_{i-1}+\dfrac{1}{q_i}$。

- **基例**：$(i=0),1$ 时由连分数定义直接成立： $\langle q_0\rangle = q_0 = \dfrac{q_0}{1} = \dfrac{n_0}{d_0}$ $\langle q_0,q_1\rangle = q_0+\dfrac{1}{q_1} = \dfrac{q_0q_1+1}{q_1} = \dfrac{n_1}{d_1}$
- **归纳假设**：假设对 $(i=k)$ 递推成立，即 $\langle q_0,\dots,q_k\rangle = \dfrac{q_k n_{k-1} + n_{k-2}}{q_k d_{k-1} + d_{k-2}}$
- **归纳步骤**：对 $(i=k)+1$，将 $q_k$ 替换为 $q_k+\dfrac{1}{q_{k+1}}$ 并代入归纳假设： $$ \begin{align*} \langle q_0,\dots,q_{k+1}\rangle &= \dfrac{\left(q_k+\dfrac{1}{q_{k+1}}\right)n_{k-1} + n_{k-2}}{\left(q_k+\dfrac{1}{q_{k+1}}\right)d_{k-1} + d_{k-2}}\[6pt] &= \dfrac{q_{k+1}(q_k n_{k-1}+n_{k-2}) + n_{k-1}}{q_{k+1}(q_k d_{k-1}+d_{k-2}) + d_{k-1}}\[6pt] &= \dfrac{q_{k+1} n_k + n_{k-1}}{q_{k+1} d_k + d_{k-1}} \end{align*} $$ 恰好符合递推形式，故对所有 $i\ge2$ 递推公式成立。

### 2. 行列式恒等式(3)的证明

$$n_i d_{i-1} - d_i n_{i-1} = (-1)^{i+1}$$ 仍用数学归纳法：

- **基例**：$(i=1)$ 时，$n_1d_0 - d_1n_0 = (q_0q_1+1)\cdot1 - q_1\cdot q_0 = 1 = (-1)^{2}$，成立。
- **归纳假设**：假设 $(i=k)$ 时成立，即 $n_k d_{k-1} - d_k n_{k-1} = (-1)^{k+1}$
- **归纳步骤**：对 $(i=k)+1$，代入递推式 $n_{k+1}=q_{k+1}n_k+n_{k-1}$、$d_{k+1}=q_{k+1}d_k+d_{k-1}$： $$ \begin{align*} n_{k+1}d_k - d_{k+1}n_k &= (q_{k+1}n_k + n_{k-1})d_k - (q_{k+1}d_k + d_{k-1})n_k\ &= n_{k-1}d_k - d_{k-1}n_k\ &= -(n_k d_{k-1} - d_k n_{k-1})\ &= -(-1)^{k+1}\ &= (-1)^{k+2} \end{align*} $$ 符合 $(i=k)+1$ 的形式，恒等式得证。

### 3. 互素结论(4)的证明

$$\gcd(n_i,d_i)=1$$ 设 $g = \gcd(n_i,d_i)$，则 $g$ 同时整除 $n_i$ 和 $d_i$，因此必然整除二者的任意整数线性组合： $$g \mid n_i d_{i-1} - d_i n_{i-1} = (-1)^{i+1}$$ 右边绝对值为1，故 $(g=1)$，即每个渐近分数天然是既约分数。

需要我给你写一个基于这套递推公式的极简Wiener攻击Python代码吗？