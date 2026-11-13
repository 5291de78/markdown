import math,random

FLAG = open('./flag').read()

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
        # 本题不需要用到更大尺寸的行列式
        return 0

def mul(a, b, x, y, z): # 矩阵乘法，a*b，其中 x,y,z 为尺寸参数
    c = [[0] * z for _ in range(x)]
    for i in range(x):
        for j in range(z):
            for k in range(y):
                c[i][j] += a[i][k] * b[k][j]
            c[i][j] %= 128
    return c
'''
det
mul

'''

def main():
    key = [[0,0,0],[0,0,0],[0,0,0]]
    while math.gcd(det(key),128) != 1:
        for i in range(3):
            for j in range(3):
                key[i][j] = random.randint(0,127)
    assert math.gcd(det(key),128) == 1
    assert len(FLAG) % 3 == 0
    assert FLAG[0:9] == "YulinSec{"
    cipher = ''
    for i in range(0, len(FLAG), 3):
        p = [[ord(FLAG[i])],[ord(FLAG[i+1])],[ord(FLAG[i+2])]]
        c = mul(key, p, 3, 3, 1)
        cipher += chr(c[0][0])
        cipher += chr(c[1][0])
        cipher += chr(c[2][0])
    print(cipher.encode().hex())

main()
