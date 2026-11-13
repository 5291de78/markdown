import socket, time

ip = "pwn.recruit.yulinsec.cn"
port = 11057

def recv_all(sock, timeout=1.0):
    buf = b""
    sock.settimeout(timeout)
    try:
        while True:
            c = sock.recv(4096)
            if not c:
                break
            buf += c
    except socket.timeout:
        pass
    sock.settimeout(None)
    return buf

sock = socket.socket()
sock.connect((ip, port))
time.sleep(0.2)
banner = recv_all(sock)
print("=== BANNER ===")
print(banner.decode(errors="replace"))

for cmd in [b"divine 2", b"divine 3", b"omen 1", b"omen 01", b"omen 2"]:
    sock.sendall(cmd + b"\n")
    time.sleep(0.3)
    r = recv_all(sock)
    print(f"--- sent {cmd!r} => {r!r} ---")

try:
    sock.sendall(b"leave\n")
except Exception:
    pass
sock.close()