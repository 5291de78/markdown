import math

FLAG = open('./flag').read()

def det(mat):
    return mat[0][0] * mat[1][1] - mat[0][1] * mat[1][0]

def mul(a, b, x, y, z): # 矩阵乘法，a*b，其中 x,y,z 为尺寸参数
    c = [[0] * z for _ in range(x)]
    for i in range(x):
        for j in range(z):
            for k in range(y):
                c[i][j] += a[i][k] * b[k][j]
            c[i][j] %= 128
    return c

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

main()
