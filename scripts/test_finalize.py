flag = "YulinSec{pray_for_me}"
hex0 = flag
print(flag.encode("ascii").hex())

def encrypt(pt: bytes) -> bytes:
    r = secrets.randbelow(len(KEY))
    prev = 0
    ct = bytearray()
    for i, value in enumerate(pt):
        current = value ^ prev ^ KEY[(i + r) % len(KEY)]
        ct.append(current)
        prev = current
    return bytes(ct)

