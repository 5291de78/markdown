import socket


if (input("mode>") == "0"):
    ip = "pwn.recruit.yulinsec.cn"
    port = 11089
else:
    ip = "127.0.0.1"
    port = 20000

sock = socket.socket()
sock.connect((ip, port))

while True:
    text = input("send>")
    sock.sendall(text.encode())
    resp = sock.recv(4096).decode()
    print(resp)




FIELD = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
GX = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
GY = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
GENERATOR = (GX, GY)