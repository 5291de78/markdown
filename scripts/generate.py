from Crypto.Util.number import *

FLAG = open('flag').read().split('\n')

def S1():
    p = getPrime(512)
    q1 = getPrime(512)
    q2 = getPrime(512)
    n1 = p * q1
    n2 = p * q2
    e1 = 257
    e2 = 65537

    m = bytes_to_long(FLAG[0].encode())
    c1 = pow(m, e1, n1)
    c2 = pow(m, e2, n2)
    print(f'n1 = {n1}')
    print(f'c1 = {c1}')
    print(f'n2 = {n2}')
    print(f'c2 = Oh no N1n3bird ate it!')

def S2():
    p = getPrime(512)
    q = getPrime(512)
    n = p * q
    e1 = 257
    e2 = 65537

    m = bytes_to_long(FLAG[1].encode())
    c1 = pow(m, e1, n)
    c2 = pow(m, e2, n)
    print(f'n = {n}')
    print(f'c1 = {c1}')
    print(f'c2 = {c2}')

S1()
print('====================')
S2()