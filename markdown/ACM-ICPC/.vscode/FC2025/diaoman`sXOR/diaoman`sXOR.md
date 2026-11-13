Problem: construct array of n distinct integers, 0 ≤ a_i ≤ 2^31-1, such that for ANY partition into two groups, XOR of both groups is equal... wait, re-read: "如果我们将数组中的所有整数随机分成两组...那么两组的按位异或和总是相等" — split all integers into two groups (one may be empty), the XOR sums of the two groups are ALWAYS equal (for any partition).

XOR of group1 = XOR of group2 for every partition. Since XOR(group1) ⊕ XOR(group2) = total XOR S. Equality of the two groups means XOR(g1) = XOR(g2), which implies S = XOR(g1) ⊕ XOR(g2) = 0. But it must hold for EVERY partition. 

If for every subset A: XOR(A) = XOR(complement) = S ⊕ XOR(A), that means XOR(A) = S ⊕ XOR(A) → S = 0. Wait that's for each partition: XOR(g1)=XOR(g2) requires XOR(g1)⊕XOR(g2) = 0 = S. So necessary: total XOR = 0. And then XOR(g2) = S ⊕ XOR(g1) = XOR(g1) automatically. So condition 3 ⟺ total XOR of all elements = 0!

Wait: for a particular partition, XOR(g1) ⊕ XOR(g2) = S always (each element appears once). XOR(g1) = XOR(g2) ⟺ XOR(g1)⊕XOR(g2) = 0 ⟺ S = 0. So if S = 0, EVERY partition has equal XORs. If S ≠ 0, NO partition works. So condition 3 ⟺ total XOR = 0.

So problem reduces: construct n DISTINCT integers in [0, 2^31-1] with total XOR = 0, or output -1.

Samples: n=5 → "5 3 4 0 2": XOR = 5⊕3⊕4⊕0⊕2 = (5⊕3=6)⊕4=2⊕0=2⊕2=0 ✓ distinct ✓.
n=3 → "1 2 3": 1⊕2⊕3=0 ✓.
n=4 → "3 2 1 0": 3⊕2⊕1⊕0=0 ✓.
n=2 → -1. Because two distinct numbers with a1⊕a2=0 impossible (a1=a2 required).

n=1: array [a1], XOR = a1 must be 0 → [0]. Distinct trivially. So answer "0"? Check condition: partitions: ({0}, {}) → XOR 0 and 0 ✓. So n=1 → 0. Hmm but is that valid? Yes.

n=2: impossible → -1.

n≥3: construction. Simple: for n even... let's think. Classic construction: 
- n odd: use 1, 2, ..., n-1 plus something? XOR of 1..m pattern.

Simple approach: 
- If n odd: output 1, 2, ..., n-2, and then x, y... hmm need distinct and XOR 0.

Alternative simple: output 0, 1, 2, ..., n-1? XOR of 0..n-1: known pattern f(m) = XOR 0..m: m%4==0→m, ==1→1, ==2→m+1, ==3→0. XOR 0..n-1 = f(n-1). Zero iff (n-1)%4==3, i.e., n%4==0. So n=4: 0,1,2,3 XOR=0 ✓ (matches sample).

General construction for n ≥ 3:
Take 1, 2, ..., n-1 and last element x = XOR(1..n-1), need x distinct from others and x ≤ 2^31-1, x ≥ 0. If x = 0 → total 0 but x=0 not in {1..n-1}, distinct ✓. If x ≥ n: distinct ✓. Problem only if x ∈ [1, n-1].

XOR(1..m) where m = n-1. For n ≥ 3, when is XOR(1..n-1) ∈ {1,...,n-1}? Often. E.g., n=5: XOR 1..4 = 4 (since f(4)=4). Sample uses different construction. n=3: XOR 1..2 = 3 ∉{1,2} ✓ works → "1 2 3" matches! n=4: XOR 1..3 = 0 → array 1,2,3,0 → distinct ✓ matches sample "3 2 1 0".

n=5: XOR(1..4)=4 ∈ {1..4} → fails. Need fix: adjust. Classic fix: if x conflicts, modify: remove two elements a,b and use a⊕b⊕x... Standard approach: if x ∈ [1,n-1], then replace: use set {1..n-1} \ {something} plus extras. 

Simple fix: choose numbers 1..n-3, then three more numbers a, b, a⊕b⊕(XOR of rest)... Let me think of a cleaner standard construction.

Standard trick: for n ≥ 3, n ≠ ... :
Let X = XOR(1..n-2). Then add last two elements: u = (1<<30), v = X ⊕ u? Wait: elements 1..n-2 plus u, v where v = X ⊕ u. Need v distinct from 1..n-2 and from u. v = X ⊕ 2^30 has the 2^30 bit set (since X < 2^30 for n ≤ 2e5), so v ≥ 2^30 > n-2, and v ≠ u since X ≠ 0. If X = 0, then v = u — conflict. Hmm.

Alternative: elements 1..n-2, u=2^30, v = X ⊕ 2^30. If X=0 then v=u conflict. Fix: pick u = 2^30, and also use 2^29: elements 1..n-3, 2^30, 2^29, w = X' ⊕ 2^30 ⊕ 2^29 where X' = XOR(1..n-3). w has bits 2^30 or 2^29 set (unless X' cancels both — X' < 2^18ish for n≤2e5, so no cancellation; w = X' ⊕ 3·2^29, which is > 2^29, distinct, and w ≠ 2^30 since X'⊕2^29 ≠ 0... w = 2^30 requires X' ⊕ 2^29 = 0 impossible since X' small; w = 2^29 requires X' ⊕ 2^30 = 0 impossible). So: output 1..n-3, 2^30, 2^29, X'⊕2^30⊕2^29. All distinct for n ≥ 3? For n=3: 1..0 empty; output 2^30, 2^29, 2^30⊕2^29 — valid but sample gives 1 2 3. Fine.

Simpler unified construction: for n ≥ 3:
- compute X = XOR of 1..n-1.
- if X == 0 or X >= n: output 1..n-1, X. Wait if X = 0, output 1..n-1, 0 — distinct ✓ total XOR = X ⊕ ... wait total = XOR(1..n-1) ⊕ X = X ⊕ X = 0. ✓. If X ≥ n: distinct ✓. If 1 ≤ X ≤ n-1: conflict.
- Conflict case: X ∈ [1, n-1]. Then remove X from the list 1..n-1 (n-2 elements), and append two elements: A = 2^30, B = (XOR of the n-2 elements) ⊕ 2^30. XOR of n-2 elements = XOR(1..n-1) ⊕ X = X ⊕ X = 0! So B = 0 ⊕ 2^30 = A. Conflict! 

Hmm. Let me redo: if we remove element X from {1..n-1}, the XOR of remaining is (XOR 1..n-1) ⊕ X = X ⊕ X = 0. Then need two distinct elements p, q ∉ remaining, with p⊕q = 0 → p = q. Impossible. So remove a different element y ≠ X: remaining XOR = X ⊕ y ≠ 0. Need p ⊕ q = X ⊕ y, p, q distinct, not in [1,n-1]\{y}, p,q ≥ 0 ≤ 2^31-1. Take p = (X⊕y) | 2^30 (set high bit to ensure ∉ [1,n-1] and ≠ 0)... q = p ⊕ (X⊕y) = 2^30 bit only: q = 2^30 if p = (X⊕y)⊕2^30. Hmm: p = (X⊕y) ⊕ 2^30, q = 2^30. p⊕q = X⊕y ✓. p ≥ 2^30 > n-1 ✓ distinct from list; q = 2^30 > n-1 ✓; p ≠ q since X⊕y ≠ 0 ✓. 

So algorithm:
- n = 1 → output 0
- n = 2 → -1
- n ≥ 3: X = XOR(1..n-1).
  - if X == 0: output 1..n-1, 0. Wait but 0 might... 0 ∉ {1..n-1} ✓. Actually simpler to just handle X==0 as X ≥ n case? X=0 < 1, not in [1,n-1] → conflict-free: append X=0. So condition: if X == 0 or X >= n → output 1..n-1 and X.
  - else (1 ≤ X ≤ n-1): remove y from list. Which y? Any y in {1..n-1}, y ≠ X (need n-1 ≥ 2, true for n≥3). Choose y = (X == 1 ? 2 : 1) — but must also ensure... p = (X⊕y)⊕2^30, q = 2^30, both fine. But wait need X⊕y ≠ 0, i.e., y ≠ X ✓. Also elements must be ≤ 2^31 - 1: 2^30 + X⊕y ≤ 2^30 + 2e5 < 2^31 ✓.
  
  Output: all of 1..n-1 except y, then p and q. Count: (n-2) + 2 = n ✓.

Check n=5: X = XOR(1..4) = 4 ∈[1,4]. y = 1 (since X=4≠1). List: 2,3,4. X⊕y = 5. p = 5⊕2^30 = 1073741829, q = 1073741824. Output: 2 3 4 1073741829 1073741824. XOR: 2⊕3⊕4 = 5; 5 ⊕ (5⊕2^30) ⊕ 2^30 = 0 ✓. Valid.

Check n=3: X = XOR(1,2) = 3 ≥ 3 → output 1 2 3 ✓ matches sample.
n=4: X = XOR(1..3) = 0 → output 1 2 3 0 ✓.

Edge: distinctness when X ≥ n: X = XOR(1..n-1) could be ≥ n — but also must be ≤ 2^31-1, obviously. But could X coincide with... it's ≥ n, list is 1..n-1, distinct ✓.

Wait, also check n=3 with X∈[1,2]? XOR(1..2)=3, not applicable. n≥3 fine.

Verify the X≥n case more: n=6: XOR(1..5) = f(5)=1? Pattern f(m): 5%4=1 → 1. So X=1 ∈[1,5], conflict. y: X==1 → y=2. List 1,3,4,5 (XOR = 1⊕3⊕4⊕5 = ... XOR(1..5)⊕2 = 1⊕2 = 3 = X⊕y ✓). p = 3⊕2^30, q=2^30. ✓.

Implementation: T up to 1e4, total n ≤ 2e5. O(n) per test.

Also double check n=1: [0], distinct, XOR=0 ✓. Is n=1 valid per problem? "其中一组可能为空" — yes works. Output "0".

Actually wait — check the problem statement sample: input "4\n5\n3\n4\n2" outputs 4 lines. Yes.

Also need to double check XOR pattern formula: f(m) = XOR 0..m: m mod 4: 0→m, 1→1, 2→m+1, 3→0. XOR(1..m) = f(m). For m=4: 4%4=0 → 4 ✓. m=5: 1 ✓. m=3: 0 ✓. m=2: 3 ✓.

Code:

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int T;
    cin >> T;
    const long long H = 1LL << 30;
    while (T--) {
        int n;
        cin >> n;
        if (n == 1) { cout << 0 << "\n"; continue; }
        if (n == 2) { cout << -1 << "\n"; continue; }
        // X = XOR(1..n-1)
        int m = n - 1, X;
        switch (m % 4) {
            case 0: X = m; break;
            case 1: X = 1; break;
            case 2: X = m + 1; break;
            default: X = 0; break;
        }
        if (X == 0 || X >= n) {
            for (int i = 1; i <= n - 1; i++) cout << i << ' ';
            cout << X << "\n";
        } else {
            int y = (X == 1 ? 2 : 1);
            long long p = (X ^ y) | H;  // = (X^y) + H since X^y small
            long long q = H;
            for (int i = 1; i <= n - 1; i++)
                if (i != y) cout << i << ' ';
            cout << p << ' ' << q << "\n";
        }
    }
}
```

Wait check p: (X⊕y) ⊕ H where H=2^30. Since X⊕y < 2^30, p = (X^y) + H. And p⊕q = X⊕y ✓. List XOR: XOR(1..n-1) ⊕ y = X ⊕ y. Total: (X⊕y) ⊕ p ⊕ q = (X⊕y) ⊕ (X⊕y⊕H) ⊕ H = 0 ✓.

Distinct: p, q ≥ 2^30 > n-1 (n ≤ 2e5) ✓; p ≠ q since X⊕y ≠ 0 ✓; y removed once ✓.

Bounds: p ≤ 2^30 + 2e5 < 2^31 - 1 ✓.

Now explain the key insight: 条件3 ⟺ 全体异或和为 0. Then construction.

Explain why n=2 impossible: a1⊕a2=0 → a1=a2 矛盾互不相同.

Write answer in Chinese.
关键是把条件 3 翻译成一句人话：**整个数组的异或和等于 0**。

## 一、条件转化

随便怎么分成两组 $G_1, G_2$，都有：

$$\text{XOR}(G_1) \oplus \text{XOR}(G_2) = \text{全体异或和 } S$$

（每个元素恰好出现一次）。而 $\text{XOR}(G_1) = \text{XOR}(G_2) \iff S = 0$。

所以：**只要总异或和为 0，任意分组的两边都相等；总异或和不为 0，怎么分都不等**。条件 3 ⟺ $a_1 \oplus a_2 \oplus \cdots \oplus a_n = 0$。

## 二、什么时候无解

- **n = 1**：输出 `0` 即可（$0$ 异或空组的 $0$ 相等）
- **n = 2**：需要 $a_1 \oplus a_2 = 0 \Rightarrow a_1 = a_2$，和"互不相同"矛盾 → **输出 -1**
- **n ≥ 3**：总能构造

## 三、构造方法（n ≥ 3）

设 $X = 1 \oplus 2 \oplus \cdots \oplus (n-1)$。

**情况 A**：$X = 0$ 或 $X \ge n$（$X$ 不在 $\{1..n-1\}$ 里）
→ 直接输出 $1, 2, \dots, n-1, X$。总和 $= X \oplus X = 0$，且互不相同 ✓

**情况 B**：$1 \le X \le n-1$（$X$ 和已有元素撞了）
→ 从 $1..n-1$ 里**删掉一个** $y \ne X$，再补两个大数：
$$p = (X \oplus y) + 2^{30}, \qquad q = 2^{30}$$
- 前 $n-2$ 个数的异或和 $= X \oplus y$（把 $y$ 从总异或里抠掉）
- $p \oplus q = X \oplus y$，两部分拼起来总异或 $= 0$ ✓
- $p, q \ge 2^{30} > n-1$，不会撞小数；$p \ne q$ 因为 $X \oplus y \ne 0$ ✓
- $p \le 2^{30} + 2\times10^5 < 2^{31}-1$ ✓

验样例：n=3 时 $X = 1\oplus2 = 3 \ge 3$ → 输出 `1 2 3` ✓；n=4 时 $X = 0$ → 输出 `1 2 3 0` ✓；n=2 → -1 ✓。

## 四、代码

$1 \oplus \cdots \oplus m$ 有 $O(1)$ 公式：按 $m \bmod 4$ 分别为 $m, 1, m+1, 0$。

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    const long long H = 1LL << 30;
    int T;
    cin >> T;
    while (T--) {
        int n;
        cin >> n;
        if (n == 1) { cout << 0 << "\n"; continue; }
        if (n == 2) { cout << -1 << "\n"; continue; }

        int m = n - 1, X;
        if (m % 4 == 0) X = m;
        else if (m % 4 == 1) X = 1;
        else if (m % 4 == 2) X = m + 1;
        else X = 0;

        if (X == 0 || X >= n) {                 // 情况 A：直接补 X
            for (int i = 1; i < n; i++) cout << i << ' ';
            cout << X << "\n";
        } else {                                 // 情况 B：删 y 补两个大数
            int y = (X == 1 ? 2 : 1);
            for (int i = 1; i < n; i++)
                if (i != y) cout << i << ' ';
            cout << ((X ^ y) + H) << ' ' << H << "\n";
        }
    }
}
```

复杂度 $O(n)$ 每组，总 $n \le 2\times10^5$，稳过。

**套路总结**：异或类构造题，先把条件翻译成一个整体不变量（这里是总异或和）；补尾元素时撞了就用"删一个小的、补两个带高位的"来腾位置——高位 $2^{30}$ 是保证不和小区间冲突的常用手法。



User wants a detailed explanation of why the construction works that way — the reasoning behind the XOR construction. Explain step by step: the design process, why 1..n-1 + X, why the conflict case, why the 2^30 trick, why delete y ≠ X, etc. Be thorough but clear.
好，这题我按"**设计者的思考路径**"来讲，你会看到每一步都是被逼出来的，不是拍脑袋。

## 第 0 步：目标回顾

要构造 $n$ 个**互不相同**的数，$0 \le a_i \le 2^{31}-1$，且总异或和为 0。

手上只有两个"旋钮"可以调：选哪些数、怎么让它们异或抵消。

## 第 1 步：最朴素的思路——"先随便放，再补一个"

异或有个天然好用的性质：**自反性**，$x \oplus x = 0$。

这启发一个万能套路：

> 先放 $n-1$ 个数，设它们的异或和为 $X$；最后一个数就放 $X$ 本身。因为
> $$X \oplus X = 0$$
> 总异或和自动归零。**不管前面放什么，最后补一个"它们的异或和"就一定满足条件 3。**

问题只剩一个：最后一个数 $X$ 可能和前面的某个数**撞车**（违反互不相同）。

所以前面 $n-1$ 个数要选一个"好算"的序列。什么序列的异或和最好算？**连续整数 $1, 2, \dots, n-1$**，因为有 $O(1)$ 公式：

$$1 \oplus 2 \oplus \cdots \oplus m = \begin{cases} m, & m \bmod 4 = 0 \\ 1, & m \bmod 4 = 1 \\ m+1, & m \bmod 4 = 2 \\ 0, & m \bmod 4 = 3 \end{cases}$$

## 第 2 步：分析什么时候撞车

补的数是 $X = 1 \oplus \cdots \oplus (n-1)$。撞车 ⟺ $X \in \{1, 2, \dots, n-1\}$。

- $X = 0$：不撞（序列从 1 开始，没有 0）→ 直接补
- $X \ge n$：比序列里所有数都大，不撞 → 直接补

这就是**情况 A**。比如 n=3，$X = 1 \oplus 2 = 3$，恰好是"下一个数"，输出 `1 2 3`，漂亮收尾。

但运气不总是这么好：n=5 时 $X = 1\oplus2\oplus3\oplus4 = 4$，**正好在序列里**，补进去就重复了。需要情况 B。

## 第 3 步：撞车了怎么办——"删一个，补两个"

现在手里有 $\{1, \dots, n-1\}$，异或和 $X$ 恰好是序列中某个数。直接补 $X$ 不行，那能不能**换掉一个数**？

思路：删掉一个数 $y$，此时剩 $n-2$ 个数，再补**两个**数 $p, q$ 凑回 $n$ 个。

删掉 $y$ 后，剩余数的异或和是多少？异或里删掉一个元素 = 再异或一次它自己：

$$\text{剩余异或和} = X \oplus y$$

要让总和为 0，补的两个数必须满足：

$$p \oplus q = X \oplus y$$

**一个方程两个未知数，自由度很大**——这就是删一个补两个的好处：把一个"必须精确等于 $X$"的死要求，变成了"两个数异或等于某值"的活要求。

## 第 4 步：$y$ 为什么不能随便删

$p \oplus q = X \oplus y$ 还有个隐藏约束：$p \ne q$（互不相同），也就是 $X \oplus y \ne 0$，即 **$y \ne X$**。

这就是代码里 `int y = (X == 1 ? 2 : 1);` 的含义——随便选个小的、但保证不等于 $X$。（你可能会问：为什么不直接删 $X$ 自己？删了 $X$ 后 $X \oplus y = 0$，就要求 $p = q$，又撞了——**这正是要避开的情形**。）

## 第 5 步：怎么选 $p, q$ 保证不和前面撞

前 $n-2$ 个数都是 $\le n-1 \le 2\times10^5$ 的小数。只要让 $p, q$ 落在"小数够不到的区间"，就天然不撞。

最省事的做法：**给一个很高的二进制位**。取 $2^{30}$：

- 它比 $n-1$（最多 20 万，约 $2^{18}$）大得多
- 又离上界 $2^{31}-1$ 有足够距离，加上小数不会溢出

具体配方：

$$q = 2^{30}, \qquad p = (X \oplus y) \oplus 2^{30} = (X \oplus y) + 2^{30}$$

（因为 $X \oplus y < 2^{18} \ll 2^{30}$，第 30 位本来就是 0，异或就等于直接加。）

验证三个要求：

1. **异或对**：$p \oplus q = (X \oplus y) \oplus 2^{30} \oplus 2^{30} = X \oplus y$ ✓（$2^{30}$ 异或两次抵消）
2. **不撞小数**：$p, q \ge 2^{30} > n-1$ ✓
3. **互不撞**：$p = q \iff X \oplus y = 0 \iff y = X$，第 4 步已经排除 ✓

## 整体回顾：设计决策链

```
补一个"异或和"让总和归零（自反性 x⊕x=0）
   ↓ 但可能撞车
选连续整数 1..n-1（异或和有 O(1) 公式，好分析）
   ↓ X = 0 或 X ≥ n 时不撞 → 情况 A
   ↓ 1 ≤ X ≤ n-1 时撞了 → 情况 B
删一个 y（y ≠ X，否则退化成 p = q），补两个 → 多一个自由度
   ↓ p, q 怎么不和前面撞？
借一个高位 2^30：离小数远、离上界也远
```

## 这道题教你的通用套路

1. **异或构造题第一工具**：$x \oplus x = 0$。"补一个异或和"是归零的万能收尾
2. **自由度不够就换元**：补一个数约束太死，就"删一补二"，把等式约束从"等于"放松成"异或等于"
3. **防撞车用高位**：当小数值域被占满时，借一个远大于它们的二进制位（$2^{30}$ 这类），等于开辟一块"无人区"
4. **先处理特殊小值**：n=1、n=2 这种边界单独讨论，往往是唯一的无解点

这套"**朴素构造 → 分析冲突 → 局部修补**"的流程，在 CF/构造题里出现频率极高，值得记下来。