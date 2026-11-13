import math


def det2(mat):
    """求二阶矩阵行列式"""
    return mat[0][0] * mat[1][1] - mat[0][1] * mat[1][0]


def adjugate_3x3(A):
    """
    输入 3×3 矩阵 A（三维列表：[[a11,a12,a13],[a21,a22,a23],[a31,a32,a33]]）
    返回伴随矩阵 adj(A)
    """
    # 代数余子式 C_ij
    c = [[0.0 for _ in range(3)] for _ in range(3)]

    # C00
    sub = [[A[1][1], A[1][2]], [A[2][1], A[2][2]]]
    c[0][0] = (+1) * det2(sub)
    # C01
    sub = [[A[1][0], A[1][2]], [A[2][0], A[2][2]]]
    c[0][1] = (-1) * det2(sub)
    # C02
    sub = [[A[1][0], A[1][1]], [A[2][0], A[2][1]]]
    c[0][2] = (+1) * det2(sub)

    # C10
    sub = [[A[0][1], A[0][2]], [A[2][1], A[2][2]]]
    c[1][0] = (-1) * det2(sub)
    # C11
    sub = [[A[0][0], A[0][2]], [A[2][0], A[2][2]]]
    c[1][1] = (+1) * det2(sub)
    # C12
    sub = [[A[0][0], A[0][1]], [A[2][0], A[2][1]]]
    c[1][2] = (-1) * det2(sub)

    # C20
    sub = [[A[0][1], A[0][2]], [A[1][1], A[1][2]]]
    c[2][0] = (+1) * det2(sub)
    # C21
    sub = [[A[0][0], A[0][2]], [A[1][0], A[1][2]]]
    c[2][1] = (-1) * det2(sub)
    # C22
    sub = [[A[0][0], A[0][1]], [A[1][0], A[1][1]]]
    c[2][2] = (+1) * det2(sub)

    # 伴随矩阵 = 代数余子式矩阵转置
    adj = list(map(list, zip(*c)))
    return adj

def det(A):
    n = len(A)
    if n == 2:
        return A[0][0] * A[1][1] - A[0][1] * A[1][0]
    elif n == 3:
        return (
              A[0][0] * (A[1][1] * A[2][2] - A[1][2] * A[2][1])
            - A[0][1] * (A[1][0] * A[2][2] - A[1][2] * A[2][0])
            + A[0][2] * (A[1][0] * A[2][1] - A[1][1] * A[2][0])
        )
    else:
        return 0

def mul(a, b, x, y, z): # 矩阵乘法，a*b，其中 x,y,z 为尺寸参数
    c = [[0] * z for _ in range(x)]
    for i in range(x):
        for j in range(z):
            for k in range(y):
                c[i][j] += a[i][k] * b[k][j]
            c[i][j] %= 128
    return c
#
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

def I_k(m):
    I = [[0 for _ in range(3)] for _ in range(3)]
    for i in range(3):
        I[i][i] = m
    return I


n = 128
m = "YulinSec{"
c = "682b623531097d6f44100553100c31234d0c2c4d4e411b01350279126021435f5a"
c = bytes.fromhex(c).decode()
C = [[0 for _ in range(3)] for _ in range(3)]
M = [[0 for _ in range(3)] for _ in range(3)]
for i in range(3):
    for j in range(3):
        M[i][j]=ord(m[3*i + j])
        C[i][j]=ord(c[3*i + j])
print(M)
print(C)
d = modinv(det(C), n)
C_adj = adjugate_3x3(C)
C_rev = mul(I_k(d) , C_adj ,3 ,3, 3)
K = mul(C_rev , M , 3 ,3, 3)
print(K)
message = ""
for i in range(0,len(c),3):
    C_0 = [[ord(c[z + i]) for z in range(3)]]
    print(C_0)
    C_1 = mul(C_0 , K , 1 ,3, 3)
    print(C_1)
    for j in range(3):
        message += chr(C_1[0][j])
print(message)







