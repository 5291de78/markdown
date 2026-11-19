

# 微积分	I 

备考建议：放轻松，然后finish them all.

## 考试宝典精选 + 错题整理

## （一）函数，极限，连续性

0**.极限的定义**

| 类型 | 定义 |
| :--- | :--- |
| 数列极限（$\varepsilon-N$ 定义） | $\lim\limits_{n\rightarrow\infty} a_n=A \Leftrightarrow \forall\varepsilon>0,\ \exists N>0$，当 $n>N$ 时，$\|a_n-A\|<\varepsilon$ |
| 函数极限（$\varepsilon-\delta$ 定义） | $\lim\limits_{x\rightarrow a} f(x)=A \Leftrightarrow \forall\varepsilon>0,\ \exists\delta>0$，当 $0<\|x-a\|<\delta$ 时，$\|f(x)-A\|<\varepsilon$ |
| 函数极限（$\varepsilon-X$ 定义） | $\lim\limits_{x\rightarrow\infty} f(x)=A \Leftrightarrow \forall\varepsilon>0,\ \exists X>0$，当 $\|x\|>X$ 时，$\|f(x)-A\|<\varepsilon$ |

### 1.极限的性质

**(1) 唯一性**：极限存在必唯一。

**(2) 保号性（3 个，主要出现在专题 3 极值点的证明处）**

① 若 $f(x)\geq g(x)$，且 $\lim f(x)=A$，$\lim g(x)=B$，则 $A\geq B$；

② 若 $f(x)\geq 0\ (\leq 0)$，且 $\lim f(x)=A$，则 $A\geq 0\ (\leq 0)$；

③ 若 $\lim\limits_{x\to a}f(x)=A>0\ (<0)$，则存在 $\delta>0$，当 $0<|x-a|<\delta$ 时……

> 注：$\lim$ 表示趋于任何数的极限，包括趋于 $a,\ a^+,\ a^-$。

> 🌸 **陷阱**：若 $f(x)>0$，且 $\lim f(x)=A$，则 $A>0$ **不**成立——只能得 $A\geq 0$，可能 $\lim\limits_{x\to\infty}f(x)=0$。

**(3) 列与子列的性质**（标题有红笔下划线，重点）

1. 如果极限存在，那么任何一个子列都有相同的极限；
2. 若 $\lim\limits_{n\rightarrow\infty} a_{2n}=\lim\limits_{n\rightarrow\infty} a_{2n+1}=A$，则 $\lim\limits_{n\rightarrow\infty} a_n=A$；
3. 要证明一个数列极限不存在，只需找到两个子列极限不相等，或至少一个子列极限不存在。

**(4) 有界性**（标题有红笔下划线，重点）

1. **数列极限的有界性**：若 $\lim\limits_{n\rightarrow\infty} a_n=A$，则存在 $M>0$ 和 $N>0$，当 $n>N$ 时，$\|a_n\|\leq M$；
2. **函数极限的局部有界性**：若 $\lim\limits_{x\rightarrow a} f(x)=A$，则存在 $\delta>0$ 以及 $M>0$，当 $0<\|x-a\|<\delta$ 时，$\|f(x)\|\leq M$。

### 2，极限的计算

![1793874096011](../计算机科学/mind_pic/1793874096011.png)

​	I,重要极限

$$
\lim_{x \to 0}(1+x)^{\frac{1}{x}}=e
$$


​	II,洛必达法则

​	III,夹逼法则

​	IV,单调有界

​	**V,麦克劳林展开式**

| 公式（$x\rightarrow 0$） | 记忆方法 |
| :--- | :--- |
| $\sin x=x-\dfrac{x^{3}}{3!}+\dfrac{x^{5}}{5!}-\cdots+\dfrac{(-1)^{n}x^{2n+1}}{(2n+1)!}+o(x^{2n+1})$ | $\sin x$ 为奇函数，因此展开式只有奇数次项 |
| $\cos x=1-\dfrac{x^{2}}{2!}+\dfrac{x^{4}}{4!}-\cdots+\dfrac{(-1)^{n}x^{2n}}{(2n)!}+o(x^{2n})$ | 记住 $\sin x$ 展开式，对其展开式求导即可 |
| $\mathrm{e}^{x}=1+x+\dfrac{x^{2}}{2!}+\dfrac{x^{3}}{3!}+\cdots+\dfrac{x^{n}}{n!}+o(x^{n})$ | $(\mathrm{e}^{x})'=\mathrm{e}^{x}$，因此 $\mathrm{e}^{x}$ 的展开式求导后形式不变 |
| $\dfrac{1}{1-x}=1+x+x^{2}+\cdots+x^{n}+o(x^{n})$ | 等比数列求和的逆用（注意 $\|x\|<1$） |
| $\dfrac{1}{1+x}=1-x+x^{2}-\cdots+(-1)^{n}x^{n}+o(x^{n})$ | 同上，并记其展开式为 $S_{n}(x)$ |
| $\ln(1+x)=x-\dfrac{x^{2}}{2}+\dfrac{x^{3}}{3}-\cdots+\dfrac{(-1)^{n+1}x^{n}}{n}+o(x^{n})$ | $[\ln(1+x)]'=\dfrac{1}{1+x}=S_{n}(x)$，对 $S_{n}(x)$ 积分即得 $\ln(1+x)$ 的展开式 |
| $\arctan x=x-\dfrac{x^{3}}{3}+\dfrac{x^{5}}{5}-\cdots+\dfrac{(-1)^{n}x^{2n+1}}{2n+1}+o(x^{2n+1})$ | $(\arctan x)'=\dfrac{1}{1+x^{2}}=S_{n}(x^{2})$，对 $S_{n}(x^{2})$ 积分即得 $\arctan x$ 的展开式 |
| $(1+x)^{a}=1+ax+\dfrac{a(a-1)}{2!}x^{2}+\cdots+\dfrac{a(a-1)\cdots(a-n+1)}{n!}x^{n}+o(x^{n})$ | 将高中学过的二项式公式推广到无穷项 |

> 至此，我们已经学习解决极限问题的 5 种方法，关于极限计算的三大题型总结在重要题型版块，建议先完成重要题型 1-3 后再学习后面的知识点。
>
> 一些问题需要灵活处理，但常见的，本质上来说的都可以归结为这五条

### 3，无穷小量的替换

.	**0 替换的本质**

等价无穷小替换的本质是 **极限乘法法则 的"分离"**。

α ~ β 的定义就是 α/β → 1，等价于 α = β·(α/β)。只有当 α 作为整式的 独立乘因 出现时，你才能把那个"极限为 1 的因子 (α/β)"干净地分离出来：

lim(f·α) = lim(f·β·(α/β)) = lim(f·β)·1 = lim(f·β)

这在乘除里天然合法。而 加法 呢？lim(f+g) = lim f + lim g 有个硬要求：f、g 各自极限都得存在。加法里没有"把比值趋于 1 的因子提出来"的操作，替换带来的误差无法被隔离，所以不能直接套。

​	**1使用前提条件（严格版）**

- 乘除因子 ：α ~ β 且 α（或 β）**是整式的独立乘因** → 可以直接换。
- 加减情形 ：一般不能换。严格判据是——设 α ~ α'、β ~ β'，则
  α ± β ~ α' ± β' 当且仅当 α 与 β 不同阶 ，即 lim(α'/β') 存在且 ≠ 1（可为 0 或 ∞，也就是这两项彼此不"等价"）。

## 函数部分

## 0,**连续与间断**

$f(x)$ 在 $x=a$ 处连续的充要条件是

$$f(a+0)=f(a-0)=f(a),$$

## ε-δ 定义

$\displaystyle\lim_{x\to x_0}f(x)=A$ 的 $\varepsilon\text{-}\delta$ 定义：
$$
\forall \varepsilon>0,\ \exists \delta>0,\ \text{当 } 0<|x-x_0|<\delta \text{ 时，恒有 } |f(x)-A|<\varepsilon\\
在某区间上连续时则
x_0 \in D
$$

**1,间断点的分类**

若 $f(x)$ 在 $x=a$ 处间断，且 $f(a+0)$ 与 $f(a-0)$ 都存在，满足

1. $f(a+0)=f(a-0)\neq f(a)$，则 $x=a$ 为 $f(x)$ 的**可去间断点**；（函数在该点不一定有定义
2. $f(a+0)\neq f(a-0)$，则 $x=a$ 为 $f(x)$ 的**跳跃间断点**。

若 $f(x)$ 在 $x=a$ 处间断，且 $f(a+0)$ 与 $f(a-0)$ 至少有一个不存在，满足

1. $\lim\limits_{x\rightarrow a} f(x)=\infty$，则 $x=a$ 为 $f(x)$ 的**无穷间断点**；
2. 除 (1) 外的其他情况，则 $x=a$ 为 $f(x)$ 的**振荡间断点**。

### 2,闭区间上连续函数的性质

1. **最值定理**　若 $f(x)\in C[a,b]$，则 $f(x)$ 在 $[a,b]$ 上一定存在最小值 $m$ 和最大值 $M$。
2. **有界定理**　若 $f(x)\in C[a,b]$，则 $f(x)$ 在 $[a,b]$ 上一定有界。
3. **零点定理**　若 $f(x)\in C[a,b]$，且 $f(a)f(b)<0$，则 $\exists\xi\in(a,b)$，使得 $f(\xi)=0$。
4. **介值定理**　若 $f(x)\in C[a,b]$，对 $\forall\eta\in[m,M]$，则 $\exists\xi\in[a,b]$，使得 $f(\xi)=\eta$。

> ⚠ **陷阱**：一定要注意区分零点定理和介值定理结论中 $\xi$ 取值的范围，前者为**开区间**，后者为**闭区间**。

### 3，无穷小量替换的实质

$$
\alpha \sim \alpha',\ \beta \sim \beta' \implies \lim\frac{\alpha}{\beta}=\lim\frac{\alpha'}{\beta'}
$$
$$
\alpha \sim \alpha' \iff \alpha = \alpha'+o(\alpha)
$$
第一行：**乘除结构极限里，无穷小可以等价替换**（前提：极限存在）
第二行：**等价无穷小的定义本质，相差一个高阶无穷小**

## （二）导数，微分

## 第 1 部分　基本概念

2.0极限的四则运算规则

**设 $\lim f(x)=A,\ \lim g(x)=B$，*极限都存在**！！，则：**

**乘除时拆分后得到的两个式子极限必须都存在才可以！**
$$
\begin{aligned}
\lim\left[f(x)\pm g(x)\right] &= \lim f(x) \pm \lim g(x) = A \pm B \\
\lim\left[f(x)\cdot g(x)\right] &= \lim f(x)\cdot \lim g(x) = A\cdot B \\
\lim\frac{f(x)}{g(x)} &= \frac{\lim f(x)}{\lim g(x)} = \frac{A}{B} \quad (B\neq 0)
\end{aligned}
$$

推论：
$$
\begin{aligned}
\lim\left[ k f(x) \right] &= k\lim f(x)=kA,\quad k\text{为常数}\\
\lim\left[ f(x) \right]^n &= \left[\lim f(x)\right]^n = A^n,\quad n\in \mathbb{N}^*
\end{aligned}
$$


### 2.1 可导性

设 $y=f(x)$ $(x\in D)$，且 $x_0+\Delta x\in D$，称 $\Delta y=f(x_0+\Delta x)-f(x_0)$ 为函数 $f(x)$ 在 $x=x_0$ 处的**增量**。

如果 $\lim\limits_{\Delta x\rightarrow 0}\dfrac{\Delta y}{\Delta x}$ 存在，称 $y=f(x)$ 在 $x=x_0$ 处**可导**，极限值称为 $y=f(x)$ 在 $x=x_0$ 处的**导数**，记为 $f'(x_0)$ 或 $\left.\dfrac{\mathrm dy}{\mathrm dx}\right|_{x=x_0}$。

如果取 $\Delta x=x-x_0$，那么 $\Delta x\rightarrow 0$ 等价于 $x\rightarrow x_0$，$\Delta y=f(x_0+\Delta x)-f(x_0)=f(x)-f(x_0)$，因此另一个等价定义为：$\lim\limits_{x\rightarrow x_0}\dfrac{f(x)-f(x_0)}{x-x_0}$ 存在，则称 $y=f(x)$ 在 $x=x_0$ 处可导。

由于极限存在的充要条件为左极限和右极限都存在且相等，$\Delta x\rightarrow 0$ 包括 $\Delta x\rightarrow 0^{+}$ 和 $\Delta x\rightarrow 0^{-}$，$x\rightarrow x_0$ 也包括 $x\rightarrow x_0^{+}$ 与 $x\rightarrow x_0^{-}$，因此：

1. $\lim\limits_{\Delta x\rightarrow 0^{+}}\dfrac{\Delta y}{\Delta x}=\lim\limits_{x\rightarrow x_0^{+}}\dfrac{f(x)-f(x_0)}{x-x_0}=f'_{+}(x_0)$，并称 $f'_{+}(x_0)$ 为 $y=f(x)$ 在 $x=x_0$ 处的**右导数**；
2. $\lim\limits_{\Delta x\rightarrow 0^{-}}\dfrac{\Delta y}{\Delta x}=\lim\limits_{x\rightarrow x_0^{-}}\dfrac{f(x)-f(x_0)}{x-x_0}=f'_{-}(x_0)$，并称 $f'_{-}(x_0)$ 为 $y=f(x)$ 在 $x=x_0$ 处的**左导数**。

$y=f(x)$ 在 $x=x_0$ 处可导的**充要条件**为：$f'_{-}(x_0)$ 与 $f'_{+}(x_0)$ 都存在且相等。

$f(x)$ 在闭区间 $[a,b]$ 上可导的充要条件是：$f(x)$ 在 $(a,b)$ 可导，且 $f'_{+}(a)$ 和 $f'_{-}(b)$ 都存在。

> **重要结论（可导必连续）**：注意到，如果函数 $f(x)$ 在 $x=x_0$ 处可导，那么根据可导的第二个定义可知极限 $\lim\limits_{x\rightarrow x_0}\dfrac{f(x)-f(x_0)}{x-x_0}$ 存在，由其分母极限 $\lim\limits_{x\rightarrow x_0}(x-x_0)=0$，那么分子极限一定为 $0$，否则该极限发散。因此 $\lim\limits_{x\rightarrow x_0}\left[f(x)-f(x_0)\right]=0$，也就是说 $\lim\limits_{x\rightarrow x_0}f(x)=f(x_0)$，根据函数连续的定义，$f(x)$ 在 $x=x_0$ 处连续。所以，有以下重要结论：如果 $f(x)$ 在在 $x=x_0$ 处可导，则 $f(x)$在此点连续   

例如：

$$\lim_{x\rightarrow 0^{+}}\frac{f(x)-f(0)}{x-0}=\lim_{x\rightarrow 0^{+}}\frac{\|x\|}{x}=\cdots$$

因此 $f(x)=\|x\|$ 在 $x=0$ 处**不可导**（左、右导数分别为 $-1$ 与 $1$，不相等）。

### 2.2 可微性
$$
\Delta y=f(x_0+\Delta x)-f(x_0)
\\
\Delta y=A\Delta x+o(\Delta x)\\
\mathrm dx = \Delta x
$$

设 $y=f(x)$ $(x\in D)$，$x_0\in D$，且 $x_0+\Delta x\in D$，称 $\Delta y=f(x_0+\Delta x)-f(x_0)$ 为函数 $f(x)$ 在 $x=x_0$ 处的增量，**如果 $\Delta y=A\Delta x+o(\Delta x)$（$A$ 为一个常数），称 $y=f(x)$ 在 $x=x_0$ 处可微**，其中 $A\Delta x$ 称为 $y=f(x)$ 在 $x=x_0$ 处的**微分**，一般记为 $\left.\mathrm dy\right|_{x=x_0}=A\,\Delta x$ 或 $\left.\mathrm dy\right|_{x=x_0}=A\,\mathrm dx$。

### 2.3,求高阶导数的方法

​	（1）归纳法

​	（2）公式法

​	（3）莱布尼茨

​	（4）泰勒展开（看系数， 中值定理，那个行列式）

### 	

# 专题 3　导数的应用、中值定理

## 3.1 极值点

### (1) 极值点的定义

（红批：此节为"定义"，重点。）

设 $y=f(x)$ $(x\in D)$，$x_0\in D$，若存在 $\delta>0$，当 $0<\|x-x_0\|<\delta$ 时，有 $f(x)<f(x_0)$，则称 $x=x_0$ 为 $f(x)$ 的**极大值点**，$f(x_0)$ 被称为**极大值**。

设 $y=f(x)$ $(x\in D)$，$x_0\in D$，若存在 $\delta>0$，当 $0<\|x-x_0\|<\delta$ 时，有 $f(x)>f(x_0)$，则称 $x=x_0$ 为 $f(x)$ 的**极小值点**，$f(x_0)$ 被称为**极小值**。

极大值点和极小值点统称**极值点**。极值点是用横坐标 $x=x_0$ 表示的，**不能称 $(x_0,\ f(x_0))$ 是极值点**。



### (2) 判断极值点的 3 个充分条件

（红批：2.1 第一充分条件——一阶导变号；2.2 第二充分条件——二阶导数定义；2.3 第三充分条件——$N$ 阶导数定义/泰勒展开。）

**第一充分条件 -- 保号性定义** 　如果存在 $\delta>0$，当 $x\in(x_0-\delta,\ x_0)$ 时，有 $f'(x)<0$，当 $x\in(x_0,\ x_0+\delta)$ 时，有 $f'(x)>0$，则 $x=x_0$ 为 $f(x)$ 的极小值点；如果存在 $\delta>0$，当 $x\in(x_0-\delta,\ x_0)$ 时，有 $f'(x)>0$，当 $x\in(x_0,\ x_0+\delta)$ 时，有 $f'(x)<0$，则 $x=x_0$ 为 $f(x)$ 的极大值点。



**第二充分条件 -- 二阶导定义**　如果函数 $f(x)$ 在 $x=x_0$ 处二阶可导，且 $f'(x_0)=0$，则当 $f''(x_0)>0$ 时，$x=x_0$ 为 $f(x)$ 的极小值点；当 $f''(x_0)<0$ 时，$x=x_0$ 为 $f(x)$ 的极大值点。

> 证明：以 $f''(x_0)>0$ 为例，$f''(x_0)>0$ 说明 $f'(x)$ 在 $x=x_0$ 附近递增（可根据极限的保号性证明），而 $f'(x_0)=0$，所以在 $x_0$ 的左邻域内 $f'(x)<0$，在 $x_0$ 的右邻域内 $f'(x)>0$，因此根据第一充分条件可知，$x=x_0$ 为 $f(x)$ 的**极小值点**。


**第三充分条件 --N阶导定义**　如果函数 $f(x)$ 在 $x=x_0$ 处 $n$ 阶可导（$n$ 为偶数），且 $f^{(k)}(x_0)=0$ $(k=1,\ 2,\ \cdots,\ n-1)$，则当 $f^{(n)}(x_0)>0$ 时，$x=x_0$ 为 $f(x)$ 的极小值点；当 $f^{(n)}(x_0)<0$ 时，$x=x_0$ 为 $f(x)$ 的极大值点。（证明不用掌握）

显然，当 $n=2$ 时，第三充分条件就是第二充分条件，因此第三充分条件是第二充分条件的拓展。例如，$y=x^4$，当 $x=0$ 时，$y'=y''=y'''=0$，但是 $y^{(4)}=24>0$，所以 $x=0$ 是 $y=x^4$ 的极小值点。

> **注**：当 $n$ 为大于 $1$ 的奇数时，无论 $f^{(n)}(x_0)$ 是正数还是负数，$x=x_0$ 都不是 $f(x)$ 的极值点。

关于求函数极值点的习题，见本专题**重要题型 1**。

## 第 2 部分　渐近线与函数作图

### 3.4 水平渐近线

> ⭐（红框）若 $\lim\limits_{x\rightarrow\infty} f(x)=A\ \Longrightarrow\ y=A$ 为水平渐近线（单侧极限成立即可，即 $x\rightarrow+\infty$ 或 $x\rightarrow-\infty$）。

### 3.5 铅直渐近线

> ⭐（红框）若 $\lim\limits_{x\rightarrow a} f(x)=\infty\ \Longrightarrow\ x=a$ 为铅直渐近线（可以对 $x\rightarrow a^{+}$ 和 $x\rightarrow a^{-}$ 分别求极限）。

### 3.6 斜渐近线

> ⭐（红框）若 $\lim\limits_{x\rightarrow\infty}\dfrac{f(x)}{x}=k$，$\lim\limits_{x\rightarrow\infty}\left[f(x)-kx\right]=b\ \Longrightarrow\ y=kx+b$ 为 $f(x)$ 的斜渐近线（单侧极限成立即可）。


### 第三部分 	中值定理
$$
\begin{aligned}
&\text{罗尔(Rolle)}: && f(a)=f(b)\implies \exists\xi\in(a,b),\ f'(\xi)=0 \\
&\text{拉格朗日(Lagrange)}: && \exists\xi\in(a,b),\ f(b)-f(a)=f'(\xi)(b-a) \\
&\text{柯西(Cauchy)}: && \exists\xi\in(a,b),\ \frac{f(b)-f(a)}{g(b)-g(a)}=\frac{f'(\xi)}{g'(\xi)}\quad(g'(x)\neq0) \\
&\text{泰勒(Taylor, 拉格朗日余项)}: && f(x)=f(x_0)+f'(x_0)(x-x_0)+\cdots+\frac{f^{(n)}(x_0)}{n!}(x-x_0)^n+\frac{f^{(n+1)}(\xi)}{(n+1)!}(x-x_0)^{n+1}
\end{aligned}
$$



## 极限计算技巧

## 1，n项化简

### 	0，简单求和：

$$
\sum_{k=1}^n k^2 = 1^2+2^2+\dots+n^2 = \frac{n(n+1)(2n+1)}{6}\\
\sum_{k=1}^n k^3 = \left[\frac{n(n+1)}{2}\right]^2
$$

2，见多识广

### 斯特林公式 Stirling
$$
n! \sim \sqrt{2\pi n}\left(\frac{n}{e}\right)^n,\quad n\to\infty\\
带余项：\\
n!=\sqrt{2\pi n}\left(\frac{n}{e}\right)^n e^{\frac{\theta_n}{12n}},\quad 0<\theta_n<1
$$
### Stolz 定理

$$
\dfrac{\infty}{\infty} 型:\{y_n\}严格单调递增,且\displaystyle\lim_{n\to\infty}y_n=+\infty,若极限\lim_{n\to\infty}\frac{x_{n+1}-x_n}{y_{n+1}-y_n}=A\\\dfrac{0}{0}型 ：\{y_n\} 严格单调递减，\displaystyle\lim_{n\to\infty}x_n=\lim_{n\to\infty}y_n=0，若
\lim_{n\to\infty}\frac{x_{n+1}-x_n}{y_{n+1}-y_n}=A\\\lim_{n\to\infty}\frac{x_n}{y_n}=A
$$

## 一些重要提醒

## 【重要题型】

### 题型 1　判断导数定义的变形是否正确

设 $y=f(x)$ $(x\in D)$，$x_0\in D$，且 $x_0+\Delta x\in D$，记 $\Delta y=f(x_0+\Delta x)-f(x_0)$，如果 $\lim\limits_{\Delta x\rightarrow 0}\dfrac{\Delta y}{\Delta x}$ 存在，称 $y=f(x)$ 在 $x_0$ 处可导。因此判断可导的关键是：极限 $\lim\limits_{\Delta x\rightarrow 0}\dfrac{\Delta y}{\Delta x}=\lim\limits_{\Delta x\rightarrow 0}\dfrac{f(x_0+\Delta x)-f(x_0)}{\Delta x}$ 是否存在。

假设 $\bar{\Delta x}$ 是 $\Delta x$ 的同阶无穷小，即 $\lim\limits_{\Delta x\rightarrow 0}\dfrac{\bar{\Delta x}}{\Delta x}=a$ $(a\neq 0,\infty)$，对原极限变形，得：

$$\lim_{\Delta x\rightarrow 0}\frac{f(x_0+\Delta x)-f(x_0)}{\Delta x}=\lim_{\Delta x\rightarrow 0}\frac{f(x_0+\bar{\Delta x})-f(x_0)}{\bar{\Delta x}}\cdot\frac{\bar{\Delta x}}{\Delta x}=\lim_{\Delta x\rightarrow 0}\frac{f(x_0+\bar{\Delta x})-f(x_0)}{\bar{\Delta x}}\cdot a$$

如果能得到 $\lim\limits_{\Delta x\rightarrow 0}\dfrac{f(x_0+\Delta x)-f(x_0)}{\Delta x}$ 存在，则 $y=f(x)$ 在 $x=x_0$ 处可导。但是，这种同阶无穷小的选取是**有讲究的**。

> **例**：$\lim\limits_{x\rightarrow 0}\dfrac{f(2-\cos x)-f(1)}{x^{2}}$ 存在，问 $f(x)$ 在 $x=1$ 处的导数存在吗？
>
> **分析**：$\lim\limits_{x\rightarrow 0}\dfrac{f(2-\cos x)-f(1)}{x^{2}}=\lim\limits_{x\rightarrow 0}\dfrac{f\left[1+(1-\cos x)\right]-f(1)}{1-\cos x}\cdot\dfrac{1-\cos x}{x^{2}}$。
>
> 根据刚刚得到的结论，由于 $x_0=1$，$\Delta x=1-\cos x$，$\bar{\Delta x}=x^{2}$，根据专题 1 的知识，当 $x\rightarrow 0$ 时，$\Delta x\rightarrow 0$，且 $\cos x\sim 1-\dfrac{x^{2}}{2}$，则 $1-\cos x$ 与 $x^{2}$ 为同阶无穷小。所以得到：$y=f(x)$ 在 $x=x_0$ 处可导。
>
> **但是上面这个结论并不正确**，问题出在忽略了 $\Delta x\rightarrow 0$ 包括 $\Delta x\rightarrow 0^{+}$ 和 $\Delta x\rightarrow 0^{-}$ 两种情况：
>
> 事实上，当 $x\rightarrow 0$ 时，$\Delta x=1-\cos x\rightarrow 0^{+}$，所以 $\lim\limits_{x\rightarrow 0}\dfrac{f(2-\cos x)-f(1)}{x^{2}}$ 存在**只能得出 $f'_{+}(1)$ 存在**，而不能说明 $f'(1)$ 是否存在。
>
> 同理，$\lim\limits_{x\rightarrow 0}\dfrac{f(1+x^{2})-f(1)}{x^{2}}$ 存在，也只能说明 $f'_{+}(1)$ 存在。
>
> 因此，在使用导数的定义判断函数是否可导之前，**一定要验证 $\Delta x\rightarrow 0$ 是否从左、右两侧都趋于 0**。

> **思考题 13**　$\lim\limits_{x\rightarrow 0}\dfrac{f(1+\sin x)-f(1)}{x}$ 或 $\lim\limits_{x\rightarrow 0}\dfrac{f(1-x)-f(1)}{x}$ 存在，能说明 $f'(1)$ 存在吗？
>
> **答案**：可以。（解析：关注微信公众号"学解"，回复"高数讲解"。）

**除了上述要注意的地方之外，还有两种情况也要引起格外的注意：**

(1) $\lim\limits_{\Delta x\rightarrow 0}\dfrac{f(x_0+\Delta x)-f(x_0-\Delta x)}{\Delta x}$ 存在**不能**得到 $f'(x_0)$ 存在。

> 反例：$f(x)=\begin{cases}2x, & x\neq 0\\ 1, & x=0\end{cases}$，在 $x_0=0$ 处，有 $\lim\limits_{\Delta x\rightarrow 0}\dfrac{f(x_0+\Delta x)-f(x_0-\Delta x)}{\Delta x}=\lim\limits_{\Delta x\rightarrow 0}\dfrac{f(\Delta x)-f(-\Delta x)}{\Delta x}=4$ 存在，但 $f(x)$ 在 $x=0$ 处不连续，所以 $f'(0)$ 不存在（可导一定连续，不连续一定不可导）。

(2) $\lim\limits_{\Delta x\rightarrow 0}\dfrac{f(x_0+2\Delta x)-f(x_0+\Delta x)}{\Delta x}$ 存在也**不能**得到 $f'(x_0)$ 存在。

> 反例：$f(x)=\begin{cases}2x+1, & x\neq 0\\ 0, & x=0\end{cases}$ 在 $x_0=0$ 处不可导，理由如下：虽然 $\lim\limits_{\Delta x\rightarrow 0}\dfrac{f(2\Delta x)-f(\Delta x)}{\Delta x}=\lim\limits_{\Delta x\rightarrow 0}\dfrac{(4\Delta x+1)-(2\Delta x+1)}{\Delta x}=2$ 存在，但 $f(x)$ 在 $x=0$ 处不连续，所以 $f'(0)$ 不存在。

以上两个反例说明：**分子上一定要保证有一个元素为 $f(x_0)$**。

如果题目中已知 $f'(x_0)$ 存在，则 $\lim\limits_{\Delta x\rightarrow 0}\dfrac{f(x_0+\Delta x)-f(x_0-\Delta x)}{\Delta x}$ 一定存在，理由如下：

$$\lim_{\Delta x\rightarrow 0}\frac{f(x_0+\Delta x)-f(x_0-\Delta x)}{\Delta x}=\lim_{\Delta x\rightarrow 0}\frac{f(x_0+\Delta x)-f(x_0)}{\Delta x}+\lim_{\Delta x\rightarrow 0}\frac{f(x_0-\Delta x)-f(x_0)}{-\Delta x}=2f'(x_0)$$

> ☆ **技巧**：利用导数的定义研究函数在一点的可导性时，一定要同时满足以下 3 个条件：
>
> 1. $\lim\limits_{\Delta x\rightarrow 0}\dfrac{f(x_0+\Delta x)-f(x_0)}{\Delta x}$ 的**分子上一定要有 $f(x_0)$ 这个元素**；
> 2. $\Delta x\rightarrow 0$ 一定要**从左、右两侧都趋于 0**；
> 3. 分子中两个增量 $\Delta x$ 与 $\bar{\Delta x}$ 是**同阶无穷小**。
>
> （旁批：① $\Delta x\rightarrow 0$ 包括 $\Delta x\rightarrow 0^{+}$ 与 $\Delta x\rightarrow 0^{-}$ 两种情况；② $a$ 不可变号。）

> **例 2-9**　设 $f(0)=1$，则 $f(x)$ 在 $x=0$ 处可导的充要条件为（　）。
>
> (A) $\lim\limits_{x\rightarrow 0}\dfrac{f(x)-\sin x}{x^{2}}$ 存在
> (B) $\lim\limits_{x\rightarrow 0}\dfrac{f(1-\mathrm e^{x})-1}{x}$ 存在
> (C) $\lim\limits_{x\rightarrow 0}\dfrac{f(1-\cos x)-1}{x^{2}}$ 存在
> (D) $\lim\limits_{x\rightarrow 0}\dfrac{f(2x)-f(x)}{x}$ 存在
>
> **解**：(A) 不满足上面技巧中的第一个条件，(C) 不满足第 2 个条件，(D) 不满足第 3 个条件，故选 **(B)**。

### 题型 2　根据导数结果求未知参数

- **性质 1**：$y=f(x)$ 在 $x=x_0$ 处可导的充要条件是 $f'_{-}(x_0)$ 与 $f'_{+}(x_0)$ 都存在且相等。
- **性质 2**：$y=f(x)$ 在 $x=x_0$ 处可导的必要条件是 $\lim\limits_{x\rightarrow x_0}f(x)=f(x_0)$（**可导必连续**）。此时代入 $f(x)$ 的表达式，分别计算两边令其相等



错题整理

小小的思考：

1，函数fx在闭区间D上连续：
​	0，fx的极值都是有界变量
​	1，fx连续absolute(fx)同样连续 **hint**:$$\left||f(x)| - |f(x_0)|\right| \le |f(x) - f(x_0)|$$




![1793873026322](../计算机科学/mind_pic/1793873026322.png)

![1793873095640](../计算机科学/mind_pic/1793873095640.png)
![1793873305807](../计算机科学/mind_pic/1793873305807.png)
![1793873364954](../计算机科学/mind_pic/1793873364954.png)
![1793873383289](../计算机科学/mind_pic/1793873383289.png)

![1793873654713](../计算机科学/mind_pic/1793873654713.png)

![1793873916948](../计算机科学/mind_pic/1793873916948.png)

注意:alarm_clock:如果分母阶数过高则考虑使用**泰勒展开**去分析



![1793875066132](../计算机科学/mind_pic/1793875066132.png)

**@breief 错在红叉标记的那一步：把极限拆成"分子的极限除以分母的极限"。**
**而分子、分母各自都趋于 0 ， 不符合极限除法的运算规则**

![1793875295136](../计算机科学/mind_pic/1793875295136.png)

**@brief可以直接用洛必达更快，但这里重要的是这种构造方法**

![1793876072276](../计算机科学/mind_pic/1793876072276.png)

![1793876510641](../计算机科学/mind_pic/1793876510641.png)
## **@brief**

积化和差
$$
\begin{align*}
\sin\alpha\cos\beta &= \dfrac12\big[\sin(\alpha+\beta)+\sin(\alpha-\beta)\big] \\
\cos\alpha\sin\beta &= \dfrac12\big[\sin(\alpha+\beta)-\sin(\alpha-\beta)\big] \\
\cos\alpha\cos\beta &= \dfrac12\big[\cos(\alpha+\beta)+\cos(\alpha-\beta)\big] \\
\sin\alpha\sin\beta &= -\dfrac12\big[\cos(\alpha+\beta)-\cos(\alpha-\beta)\big]
\end{align*}
$$
和差化积
$$
\begin{align*}
\sin A + \sin B &= 2\sin\dfrac{A+B}{2}\cos\dfrac{A-B}{2} \\
\sin A - \sin B &= 2\cos\dfrac{A+B}{2}\sin\dfrac{A-B}{2} \\
\cos A + \cos B &= 2\cos\dfrac{A+B}{2}\cos\dfrac{A-B}{2} \\
\cos A - \cos B &= -2\sin\dfrac{A+B}{2}\sin\dfrac{A-B}{2}
\end{align*}
$$

![1793876642639](../计算机科学/mind_pic/1793876642639.png)

![1793876656851](../计算机科学/mind_pic/1793876656851.png)
![1793876802401](../计算机科学/mind_pic/1793876802401.png)
**@brief 有些数列的单调并不简单！建议使用蛛网图观察数列走向，灵活构造**

![1793876969520](../计算机科学/mind_pic/1793876969520.png)

![1793877136693](../计算机科学/mind_pic/1793877136693.png)

**@brief 局部保号性的使用！！！函数闭区间连续的定义**

![1793877195589](../计算机科学/mind_pic/1793877195589.png)

![1793877352859](../计算机科学/mind_pic/1793877352859.png)

![1793877368373](../计算机科学/mind_pic/1793877368373.png)

要证明连续 就的回想**连续的定义** ，单调性构造了不等式，想到了**夹逼证明**！

![1793877385641](../计算机科学/mind_pic/1793877385641.png)

静下心来，好好感受题目的意思

![1793877396538](../计算机科学/mind_pic/1793877396538.png)


![2135B63514FCA3BF742BFE7012A2C4B1](../计算机科学/mind_pic/2135B63514FCA3BF742BFE7012A2C4B1.jpg)
![1793716012253](../计算机科学/mind_pic/1793716012253.png)

**（3）** 设 $f(x)$ 在点 $x_0$ 可导，则当 $\Delta x\rightarrow 0$ 时，$f(x)$ 在点 $x_0$ 处的 $(\Delta y-dy)$ 是（学生选 **C**）.

A、与 $\Delta x$ 同阶但不等价的无穷小；
B、$\Delta x$ 的等价无穷小；
C、比 $\Delta x$ 高阶的无穷小；
D、比 $\Delta x$ 低阶的无穷小.
> 红笔推导：$dy=f'(x_0)\Delta x$（$\Delta x=dx$），$\Delta y=f(x_0+\Delta x)-f(x_0)=f'(x_0)\Delta x+o(\Delta x)$，故 $\Delta y-dy=o(\Delta x)$.
> 
**2.** 下列命题中正确的是（学生圈选 **B**）.

(A) 无界变量必为无穷大量；
(B) 有限多个无穷大量之和仍然为无穷大量；
(C) 无穷大量必为无界变量；
(D) 无穷大量与有界变量之积仍然为无穷大量.

> 红笔：A 处划改，写反例 $\dfrac{1}{x}\sin\dfrac{1}{x}$；另有 "$f(x)-x=0$!"、“无界 $\rightarrow$ 数列！！” 等批注（部分辨认不清）
> 
**5.** 设 $f(0)=0$，则 $f(x)$ 在 $x=0$ 处可导的充要条件为（学生先圈 D 后改 **B**）.

A. $\lim\limits_{h\rightarrow 0}\dfrac{1}{h^2}f(1-\cos h)$ 存在；
B. $\lim\limits_{h\rightarrow 0}\dfrac{1}{h}f(1-\mathrm e^{h})$ 存在；
C. $\lim\limits_{h\rightarrow 0}\dfrac{1}{h^3}f(h-\sin h)$ 存在；
D. $\lim\limits_{h\rightarrow 0}\dfrac{1}{h}\left[f(2h)-f(h)\right]$ 存在.

> 红笔："$h\rightarrow 0^{+}$ 只有一种情况"、"$h-\sin h\sim \frac{1}{6}h^3$"、"$f(0)$ 为何？？" 等.
> 
**3.（清华 2013）** 设 $f(x)$ 在区间 $[a,b]$ 上 3 阶可导，且在 $[a,b]$ 上 $\|f'''(x)\|\leq M$，

$$f(a+h)=f(a)+f'\left(a+\frac{h}{2}\right)h+E(h),\quad (0<h<b-a)$$

其中 $E(h)$ 为误差项。求证：$\|E(h)\|\leq\dfrac{7}{24}Mh^3$.

> 红笔圈注：$(a,\ a+h]\subset(a,b]$；圈 "1/4"；写 "$\frac{1}{2}f''(a)=E(h)/h^2$"（?）.

> **注：比较特殊的构造**：①形如 $\dfrac{f''(x)}{g''(x)}=\dfrac{f(x)}{g(x)}$ 的函数构造为
> $$F(x)=f'(x)g(x)-f(x)g'(x).$$（红框）

## 二、分析题（每小题 4 分，共 4 分）

**1.** $\lim\limits_{x\rightarrow 0}x\sin\dfrac{1}{x}=\lim\limits_{x\rightarrow 0}x\cdot\lim\limits_{x\rightarrow 0}\sin\dfrac{1}{x}=0$ 正确吗？如果不正确，请说明原因，并说明正确的运算方法.

> 红笔：极限的乘积法则要求两个极限都存在（此处 $\lim\sin\frac{1}{x}$ 不存在）.

## 三、八（共 4 分）

设 $m、n$ 均为正数，且 $x\rightarrow 0$，请解答以下问题：

(1) 试判断下面等式的正确性：

$$(A)\quad o(x^m)-o(x^n)=0;\qquad (B)\quad o(x^m)\,o(x^n)=o(x^{m+n}).$$

(2) 错误的请举例说明.

> 红笔："有几个？"；圈画 "$x-\ln x$" 字样（?）；下方写 "(A) 正确"（?）.

## 四、八（共 8 分）【证明题】

设 $f(x),\ g(x)$ 在 $[a,b]$ 上可导，且 $g'(x)\neq 0$，证明：$\exists\xi\in(a,b)$，使得

$$\frac{f(a)-f(\xi)}{g(\xi)-g(b)}=\frac{f'(\xi)}{g'(\xi)}.$$

## 五、九（共 6 分）【证明题】

设函数 $f(x)$ 在区间 $[0,1]$ 上连续，在 $(0,1)$ 内可导，且 $f(0)=f(1)=0$，$f\left(\dfrac{1}{2}\right)=1$，试证对任意实数 $\lambda$，必存在 $\xi\in(0,1)$，使得

$$f'(\xi)-\lambda\left[f(\xi)-\xi\right]=1.$$

> 红笔：令 $F(x)=\mathrm e^{-\lambda x}(f(x)-x)$；改写结论 $f'(\xi)-\lambda f(\xi)+\lambda\xi-1=0$.

## 六、九、证明题 2（每小题 6 分，共 6 分）

**1.** 设 $f(x)$ 在闭区间 $[0,1]$ 上有三阶导数，且 $f(0)=f(1)=0$，令 $F(x)=x^3f(x)$。求证 $\exists\xi\in(0,1)$ 使得 $F'''(\xi)=0$.

> 红笔："$F''(0)=F''(1)$"（?），箭头引导.

**2.** 设 $f(x)$ 在闭区间 $[-1,1]$ 上存在二阶导数，对 $\forall x\in(-1,1)$，有 $f'(-x)=f'(x)$，且 $f(0)=0,\ f(1)=1$，求证：$\exists\xi\in(-1,1)$，使得 $f''(\xi)+f'(\xi)=1$.

> 红笔：$F(x)=\mathrm e^{x}\left[f'(x)-1\right]$（?）.

## 附：手写解答页（辨认整理）

**1. 极限题推导链：**

$$\left(\frac{a_1^n+a_2^n+\cdots+a_m^n}{m}\right)^{\frac{a}{n}}
=\left(1+\frac{\sum\limits_{i=1}^{m}(a_i^n-1)}{m}\right)^{\frac{a}{n}}
=\exp\left(a\cdot\frac{\ln\left(1+\frac{1}{m}\sum\limits_{i=1}^{m}\left(\mathrm e^{n\ln a_i}-1\right)\right)}{n}\right)$$

$$=\exp\left(a\cdot\frac{\frac{1}{m}\,n\ln\prod\limits_{i=1}^{m}a_i}{n}\right)=\left(\prod_{i=1}^{m}a_i\right)^{\frac{a}{m}}.$$

> 旁注：$(ab)^{\frac{3}{2}}$（?）.

**2. 分析题 3 的手写证明**（按 $\varepsilon-\delta$ 定义证明 $\dfrac{1}{f(x)}\in C(a,b)$，其中 $f$ 在 $(a,b)$ 连续且恒正）：

> 设 $f(x)$ 在 $(a,b)$ 上连续且恒大于 0，按 $\varepsilon-\delta$ 定义证明 $\frac{1}{f(x)}\in C(a,b)$。
> 证：$\forall x_0\in D$，取 $\varepsilon_1=\frac{1}{2}f(x_0)$，$\exists\delta_0>0$，当 $0<\|x-x_0\|<\delta_0$ 有 $\|f(x)-f(x_0)\|<\frac{f(x_0)}{2}\implies f(x)>\frac{f(x_0)}{2}$。
> $\therefore \left\|\frac{1}{f(x)}-\frac{1}{f(x_0)}\right\|=\frac{\|f(x)-f(x_0)\|}{f(x)f(x_0)}<\frac{2\|f(x)-f(x_0)\|}{f^2(x_0)}$。
> $\therefore \exists\delta_1>0$，当 $0<\|x-x_0\|<\delta_1$ 有 $\|f(x)-f(x_0)\|<\frac{f^2(x_0)}{2}\cdot\varepsilon_1$。
> 取 $\delta_2=\min\{\delta_0,\delta_1\}$，则 $\left\|\frac{1}{f(x)}-\frac{1}{f(x_0)}\right\|<\varepsilon$，成立。

**3. 分析题 4 的手写思路**（$f''(x_0)$ 不存在但 $\lim\limits_{h\rightarrow 0}\dfrac{f(x_0+h)+f(x_0-h)-2f(x_0)}{h^2}$ 存在的例子）：

> Hint：$f''(x_0)$ 不存在，即 $\lim\limits_{x_0\rightarrow 0^{+}}\left[f'(x_0)\right]'\neq\lim\limits_{x_0\rightarrow 0^{-}}\left[f'(x_0)\right]'$。
> 分段构造：$f''(x_0)=\begin{cases}c_1, & x>0\\ c_2, & x<0\end{cases}$，$f'(x_0)=\begin{cases}c_1x, & x>0\\ c_2x, & x<0\end{cases}$，$f(x_0)=\begin{cases}c_1x^2, & x>0\\ c_2x^2, & x<0\end{cases}$。
> 验证：$\lim\limits_{h\rightarrow 0^{+}}\frac{c_1h^2+c_2(-h)^2}{h^2}=\lim\limits_{h\rightarrow 0^{-}}\frac{c_1(-h)^2+c_2h^2}{h^2}=c_1+c_2$，两侧相等，极限存在。

**3.** 设 $x_n=\left(1+\dfrac{1}{2^2}\right)\left(1+\dfrac{1}{2^4}\right)\cdots\left(1+\dfrac{1}{2^{2^n}}\right)$，求 $\lim\limits_{n\rightarrow\infty}x_n$.

**8.** 记 $f(x)=\lim\limits_{n\rightarrow\infty}\dfrac{x^{2n-1}+a+bx}{x^{2n}+1}$，$n$ 为自然数，确定常数 $a,\ b$，使得 $f(x)$ 为 $\mathbb{R}$ 上的连续函数.

> 红批：圈出分子中的 $x^{2n-1}$ 与整体分式（意在按 $\|x\|$ 与 $1$ 的大小分段讨论极限）.



**10.** 设函数 $f(x)=x-\left(a+b\,\mathrm e^{x^{2}}\right)\sin x$ 当 $x\rightarrow 0$ 时是 $x$ 的**五阶无穷小量**，求常数 $a,\ b$ 的值.

> 红批：**加减中不可用等价无穷小，用泰勒展开**（把 $\mathrm e^{x^2}$ 与 $\sin x$ 展开到足够阶，令低阶系数全为零）.

**12.** 求函数 $f(x)=\sin\left(x^{2}+2\sqrt{\pi}\,x\right)$ 在 $x=-\sqrt{\pi}$ 的 $n$ 阶导数.

> 红批：配方 $\sin\left((x+\sqrt{\pi})^{2}-\pi\right)$；令 $t=x+\sqrt{\pi}$，化为 $f=-\sin t^{2}$ 再求导.

**15.** 设 $f(x)$ 在 $[0,1]$ 上有二阶导数，且 $\|f''(x)\|\leq 1$，如果 $f(x)$ 在 $(0,1)$ 上有最大值，证明
$$\|f'(0)\|+\|f'(1)\|\leq 1.$$

> 红批：提到"泰勒中值定理"不要乱用.

**15（另一题）.** 设 $f(x)=x\ln\left(x+\sqrt{1+x^{2}}\right)$，求 $f^{(2014)}(0)$ 的值..