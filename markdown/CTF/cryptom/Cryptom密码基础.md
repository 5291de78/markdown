# Cryptom密码基础

## 	1RSA

# RSA 快速复习（极简版，适合竞赛/CTF）

> RSA 是非对称加密：**公钥加密，私钥解密；私钥签名，公钥验签** 核心：大整数分解困难。

## 1. 密钥生成（重点）

1. 选两个**不同的大素数** $(p,q)$

2. 计算模数： $$n = p \times q$$

3. 欧拉函数： $$\varphi(n)=(p-1)(q-1)$$

4. 选公钥指数 $e$，满足： $$1<e<\varphi(n),\quad \gcd(e,\varphi(n))=1$$

   > 常用 $(e=65537)$（0x10001），速度快、不容易踩坑

5. 求私钥 $d$：$e$ 在模 $\varphi(n)$ 下的逆元 $$e\cdot d \equiv 1 \pmod{\varphi(n)}$$ 也就是： $$d = e^{-1} \bmod \varphi(n)$$

✅ 公钥：$((e,n))$ 公开 ✅ 私钥：$((d,n))$ 保密（$(p,q),\varphi(n)$ 也保密）

## 2. 加密

明文 $m$（必须满足 $(0<m<n)$） $$c = m^e \bmod n$$ $c$：密文

## 3. 解密

$$m = c^d \bmod n$$

## 4. 原理一句话

因为 $ed\equiv 1 \pmod{\varphi(n)}$，设 $ed = k\varphi(n)+1$ $$c^d = (m^e)^d = m^{ed}=m^{k\varphi(n)+1}=(m^{\varphi(n)})^k \cdot m \overset{\text{欧拉定理}}{\equiv} m \pmod{n}$$

> 欧拉定理：若 $\(\gcd(m,n)=1)$，则 $m^{\varphi(n)}\equiv 1\pmod{n}$ 即使 $\gcd(m,n)\neq1$，RSA 依然成立（这个是拓展，CTF一般不用背）

## 5. 签名（和加密反过来！高频考点）

- 签名：用私钥算 $s = m^d \bmod n$

- 验签：用公钥算 $m' = s^e \bmod n$，对比 $m'$ 和原文哈希

  > 区分口诀：**加密：公钥加密；签名：私钥签名**

## 6. 常见坑 & CTF 考点

1. $m \ge n$：加密失败，明文不能大于等于模数
2. $e$ 很小（比如 $(e=3)$）：容易爆破（广播攻击、小指数攻击）
3. 知道 $(p,q)$ 就能算出 $\varphi(n)$，算出 $d$ → 分解n是RSA最大威胁
4. 不要直接对长明文RSA！RSA只适合短数据；实际是 **RSA加密AES密钥，AES加密正文（混合加密）**
5. 原始RSA（无填充）不安全：**教科书RSA**，有同态、可移位攻击；真实场景用 OAEP 填充

## 7. Python 极简代码（教科书RSA，仅学习，不用于真实加密）

```python
import math

def egcd(a, b):
    if b == 0:
        return (a, 1, 0)
    else:
        g, x, y = egcd(b, a % b)
        return (g, y, x - (a // b) * y)

def modinv(a, m):
    g, x, y = egcd(a, m)
    if g != 1:
        raise Exception('无逆元')
    else:
        return x % m

p = 61
q = 53
n = p * q
phi = (p-1)*(q-1)
e = 65537
d = modinv(e, phi)

m = 123
c = pow(m, e, n)   # 加密
m2 = pow(c, d, n)  # 解密
print(c, m2)
```

> `pow(a,b,mod)` Python内置，高效，CTF必用！

## 8. 速记卡片

- $n=p\cdot q$
- $\varphi(n)=(p-1)(q-1)$
- $\gcd(e,\varphi)=1$
- $d=e^{-1}\bmod\varphi$
- $c=m^e \bmod n$
- $m=c^d \bmod n$

要不要我出2道口算小题帮你自测？

### 工具

```
#逆元计算
```



```python
import gmpy2
from Crypto.Util.number import *
	primes(n)		#返回一个大于n的素数 右值
from sympy import factorint
	factorient(n) = {}   #返回字典{}
    	primes = list(factorint(n).keys()) 
#多个模数
	#GCD attack
	p = gcd(n1, n2)			 
    # 共模攻击 
    s1 = int (invert(e1, e2)) 
	s2 = ( 1 - s1 * e1) // e2 	#同一个`n` ，两对不同`(e, c)` ，且`gcd(e1, e2) == 1`
	m = ( pow (c1, s1, n) * pow (c2, s2, n)) % n
#加密
e = 257			#一般情况是65537
m = bytes_to_long(FLAG) #将明文转换为10binary
p = getPrime(512) ，q = getPrime(512)
d = inverse(e,(p-1)*(q-1))					#	     public key  = { n , e} 
n = p*q			 #n就是RSA的模数						private key = {p,q, d}
c = pow(m , e , n)  #加密
#模数分解方法
'''
1，一般只会给n 和 e
拿到 n
  │
  ├─ 去 factordb 查 → 有记录？ → 直接拿到 p, q
  │
  ├─ 没记录 → 试 sympy.factorint (小因子)
  │
  ├─ 试 Fermat (p≈q)
  │
  ├─ 试 Pollard p-1 (p-1 平滑)
  │
  ├─ 试 YAFU (通用, 中等大小)
  │
  └─ CADO-NFS (最后手段, 很慢)
'''
#解密
m = pow(c, d, n)
flag = long_to_bytes(m)



```

# 例题

```python
#GCD攻击 与 共模攻击
import gmpy2
from math import gcd
from Crypto.Util.number import *
from sympy import factorint
e1 = 257
e2 = 65537
n1 = 102841764361706290711537358442958510039972178758365835199586465418978764244063070347547822658913799623398509950628429862440110552308464359458913745289848918991216401601401162790197780388298263471303426483963898263604850626042813348440673661197944367136113798378705225980098656834022671825261421780755839717301
c1 = 71408898863342331968822348687265076066946445538002150582274971106270402651320915665161367130756610706545169694476885329210683087775076765020249313837509974756150747712555149876157933026393638634470176959570321286772429484105930953268977864795387937055501698111283687530160781845353098203666485179007190830107
n2 = 69628981484140144947871002558113746274287920294740027234484066104125383116166939298435045897499843376954506110525317597553486488755669980688499809946898589971000621258764290711345459794543130610502890628834880991539982341920156676314088248435865106236792102738406632875713602685492774671179558948725235757159
p = gcd(n1, n2)
q1 = n1//p
m = pow(c1 , inverse(257 , (p-1)*(q1-1)) ,n1)
flag1 = long_to_bytes(m)
n = 56332412999908807156310322236839909076241211583149526662243282361473515166188547920164585264269508063965348263095122266092367718399545103834798357450403138402917548972688689727255445681991069756182784144304638348677143808321856631062556648974285712222061720463679982828985581131018527153233130839076306347821
c1 = 19964294676843197852923921338688362631656890640637128211480322451650356210592316203030907927119156672389441818248881475936816380166450708853878764821867434554543777350987160742683517481024795389573937676412987214583259893368085798101838653648337782296666045370523428942187474238478570786325907234287534040509
c2 = 27516728508158959955250008788111253149344350713341565423702888877982839511880426457994098785693726974519387492408873109565389876154998253093333262587294263954003239361532448046363494313578730868905763814397184766103305616319627008180747369538525305936753857737984343301302739869200917848270512411042362811752
s1 = int (inverse(e1, e2))
s2 = ( 1 - s1 * e1) // e2
m = ( pow (c1, s1, n) * pow (c2, s2, n)) % n
flag2 = long_to_bytes(m)
print(flag1 + flag2)

```

## 线性代数与希尔加密

$$
加密：c \equiv K  p \pmod{m}   
\\解密：p \equiv K^{-1} c\pmod{m}
$$

一句话：

K为密钥举证  m为密码本长度（如果起始编码从0开始）

```python
import math
#矩阵乘法
def mul(a, b, x, y, z):
    c = [[0] * z for _ in range(x)]
    for i in range(x):
        for j in range(z):
            for k in range(y):
                c[i][j] += a[i][k] * b[k][j]
            c[i][j] %= 128
    return c

# 密文hex还原
raw_bytes = bytes.fromhex("396c5b676d4f0b52032c15033e0157323f3610417d4536136d306d29091a1c0c306f216c")

#encode
def main():
    key = [[2,11],[5,19]]
    assert math.gcd(det(key),128) == 1
    assert len(FLAG) % 2 == 0
    cipher = ''
    for i in range(0, len(FLAG), 2):
        p = [[ord(FLAG[i])],[ord(FLAG[i+1])]]
        c = mul(key, p, 2, 2, 1)
        cipher += chr(c[0][0])
        cipher += chr(c[1][0])
    print(cipher.encode().hex())

# mod128下算出的K^{-1}
inv_key = [[29, 91],
           [53, 30]]

#decode
FLAG = ""
for i in range(0, len(raw_bytes), 2):
    c0 = raw_bytes[i]
    c1 = raw_bytes[i+1]
    c = [[c0], [c1]]
    # p = inv_key * c mod128
    p = mul(inv_key, c, 2, 2, 1)
    p0 = p[0][0]
    p1 = p[1][0]
    FLAG += chr(p0) + chr(p1)
print(FLAG)

```

K^{-1}的具体计算方法：
$$
(\boldsymbol{K}= \begin{bmatrix}2 &11\\5 &19\end{bmatrix},\ m=128)

\\1. \det(K)=-17
\\2. \gcd(-17,128)=1，存在模逆：-17^{-1}\equiv15\pmod{128}
\\3. 伴随矩阵 \boldsymbol{K}^*=\begin{bmatrix}19 & -11\\-5 & 2\end{bmatrix}
\\4. \boldsymbol{K}^{-1}=15\cdot\boldsymbol{K}^* \pmod{128}

\boldsymbol{K}^{-1}=
\begin{bmatrix}
29 & 91 \\
53 & 30
\end{bmatrix}
\\5. 每组密文向量 \boldsymbol{c}，计算 \boldsymbol{p}=K^{-1}\boldsymbol{c}\pmod{128}，得到明文向量。
$$
​	模逆 
$$
-17 \cdot x \equiv 1 \pmod{128}
\\-17 \equiv 128 -17 = 111 \pmod{128}
\\111x \equiv 1 \pmod{128}
\\现在问题转化：求 111 在模 128 下的乘法逆元。
\\扩展欧几里得算法:给定 (a,m)，找整数 (x,y) 满足:ax+my = \gcd(a,m)
$$

```python
def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    else:
        g, x, y = extended_gcd(b % a, a)
        return g, y - (b // a) * x, x

def modinv(a, m):
    g, x, y = extended_gcd(a, m)
    if g != 1:
        raise Exception("模逆不存在")
    return x % m

print(modinv(-17, 128))
# 输出：15

```


不是。顺序和细节有两处错，正确流程是：

**正确步骤**
1. 算 `d = det(K) mod n`，确认 `gcd(d, n) = 1`（否则矩阵不可逆，不能解密）
2. 算 `d` 的**模逆** `d⁻¹`（即 `d·d⁻¹ ≡ 1 (mod n)`，用扩展欧几里得）
3. 算**伴随矩阵** `adj(K)`（即"一般逆矩阵公式里那个整数矩阵"，`adj(K) = det·K⁻¹`，每个元都是整数）
4. `K⁻¹ = d⁻¹ · adj(K)`，最后对**每个元取 mod n**

**你描述里的两个错**
- **"先算一般逆矩阵再对每个元取模"不行**：一般逆矩阵 `adj(K)/det` 的元是分数，mod 对分数没有定义。能取模的是伴随矩阵的整数元。
- **"再数乘 det"错了**：应该乘的是 **det 的模逆 d⁻¹**，不是 det 本身。

记忆法：`K⁻¹ ≡ d⁻¹ · adj(K) (mod n)` —— 模世界里"除以 det"要翻译成"乘 det 的模逆"。

例子（n=26）：
```
K = [[3,3],[2,5]]
det = 9，9⁻¹ mod 26 = 3（因为 9·3=27≡1）
adj(K) = [[5,-3],[-2,3]]
K⁻¹ = 3·[[5,-3],[-2,3]] mod 26 = [[15,17],[20,9]]
```

# 

### 		

