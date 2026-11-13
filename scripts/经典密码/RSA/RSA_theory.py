from Crypto.Util.number import *

m = "YulinSec{Basic_RSA_1113}"
e = 65537
p = getPrime(512)
q = getPrime(512)
n = p*q
phi = (p - 1) * (q - 1)
d = pow(e, -1, phi )
m2 = int.from_bytes(bytes.fromhex(m), "big")
m = bytes_to_long(m.encode())
'''
print(m)
print(m2)
'''

c = pow(m, e, n)
print(c)
flag = pow(c,d,n)
print(long_to_bytes(flag))
