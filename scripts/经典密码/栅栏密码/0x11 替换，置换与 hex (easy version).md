# 0x11 替换，置换与 hex (easy version)

```python
substitution = ['h', 'k', 'S', 'A', 'D', 'm', 'G', 'O', 'o', 'L', 'E', 'b', 'l', 'M', 'K', 't', 'X', 'f', 'Q', 'j', 'z', 'U','g', 'c', 'v', 'u',
       'F', 'C', 'e', 'n', 'B', 'J', 'P', 'I', 'V', 'N', 'Z', 'i', 'q', 'a', 'W', 'H', 'p', 'R', 'w', 'T', 'r', 'Y', 'd', 'x', 's', 'y']
cipher1 = ''
for ch in flag:
    if 'A' <= ch <= 'Z':
        idx = ord(ch) - ord('A')
        cipher1 += substitution[idx]
    elif 'a' <= ch <= 'z':
        idx = ord(ch) - ord('a') + 26
        cipher1 += substitution[idx]
    else:
        cipher1 += ch

cipher2 = ''
for j in range(3):
    for i in range(len(flag)//3):
        cipher2 += cipher1[i*3+j]

print(cipher2.encode().hex())

```

这道题使用了两道加密工序，也就是cipher1和cipher2，cipher1采用了一个自制的密码本，具体来说就是将大写字母映射到了这个表的前26个，小写字母则映射到后26个。

那等我们解出cipher2之后就只用查表映射即可

```
list = [A,B,C,D。。。。] #大致意思就是上面subs的对应表
flag = ""
for i in cipher:
	flag += substitution.index(i)
```

而cipher2就是一个分了三栏的栅栏密码

只需要

```python
    m = len(cipher2) // 3
    col0 = cipher2[0:m]
    col1 = cipher2[m:2*m]
    col2 = cipher2[2*m:]
    plain = ""
    for i in range(m):
        plain += col0[i] + col1[i] + col2[i]
```

即可