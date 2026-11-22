from Crypto.Util.number import *

m = "YulinSec{Basic_RSA_1113}"
e = 65537
p = getPrime(512)
q = getPrime(512)
n = p*q
phi = (p - 1) * (q - 1)
d = pow(e, -1, phi )
m = bytes_to_long(m.encode())
'''
print(m)
print(m2)
'''
print(f"e:{e}\npub_key:{n}\npriv_key:{d}\n")
c = pow(m, e, n)
flag = long_to_bytes(pow(c,d,n))
print(f"encrypto:{c}\ndecrypt:{flag}")

