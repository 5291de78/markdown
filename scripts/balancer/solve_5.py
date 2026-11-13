import socket
import re


import random
REG_MASK = (1 << 256) - 1
def local_check(cmd):
    assert cmd.endswith(";") and len(cmd) <= 2500, "结尾/长度不符"
    stmts = cmd[:-1].split(";")
    assert all(__import__("re").fullmatch(r"([AB])=([AB]|\d+)(\+|-|\*|//|<<|>>|&|\^|%)([AB]|\d+)", s) for s in stmts), "语法错误(空格/括号/非法符号)"
    step = 16
    for s in stmts:
        op = s.translate(str.maketrans("", "", "=AB0123456789"))
        if op in (">>", "<<", "+", "-", "&", "^"): step -= 1
        elif op in ("*", "//", "%"): step -= 3
        else: raise ValueError(f"坏运算符: {op!r}")
    print("剩余步数:", step); assert step >= 0
    for _ in range(1000):
        A0 = random.getrandbits(256); env = {"A": A0, "B": 0}
        for s in stmts:
            exec(s, env); env["A"] &= REG_MASK; env["B"] &= REG_MASK
        assert env["A"] == A0.bit_count(), f"算错了: {env['A']} != {A0.bit_count()}"
    print("本地自测 1000 组通过")


def recv_all(sock, timeout=2):
    buf = b""
    sock.settimeout(timeout)
    try:
        while True:
            try:
                chunk = sock.recv(4096)
            except (ConnectionResetError, ConnectionAbortedError):
                break            # 对端 RST：不抛异常，用已收到的数据
            if not chunk:
                break            # 对端正常关闭
            buf += chunk
    except socket.timeout:
        pass
    sock.settimeout(None)
    return buf.decode("utf-8", errors="replace")

def recv_until(sock, marker=b"> ", timeout=5):
    buf = b""
    sock.settimeout(timeout)
    while marker not in buf:
        try:
            chunk = sock.recv(4096)
        except (ConnectionResetError, ConnectionAbortedError):
            break
        if not chunk:
            break
        buf += chunk
    sock.settimeout(None)
    return buf


def send_line(sock, msg):
    msg = str(msg) + '\n'
    sock.sendall(msg.encode("utf-8"))
'''
B=A>>1;B=B&M0;A=A-B;            (3步)  减法技巧：2bit字段 v−(v>>1)=popcount(v)
B=A>>2;B=B&M1;A=A&M1;A=A+B;     (4步)  折成 4bit 字段 ≤4
B=A>>4;B=B&M2;A=A&M2;A=A+B;     (4步)  折成 8bit 字段 ≤8
A=A*K;                          (3步)  K=00000001×32，32字节并行求和
A=A>>248;                       (1步)  结果落到低8位
'''

mode = [("pwn.recruit.yulinsec.cn" , int(input("port_NUM>"))) , ("127.0.0.1" , 20000)]
dece = input("local_0 or remote_1>")
if dece == '1':
    ip , port = mode[0]
else:
    ip , port = mode[1]
print(ip + '\n' +  str(port))

'''
def recv_all(sock, timeout=1):
    buf = b""
    sock.settimeout(timeout)
    try:
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            buf += chunk
    except socket.timeout:
        pass
    sock.settimeout(None)
    return buf.decode("utf-8", errors="replace")
'''


M0 = int('5'*64, 16)    # 2bit 掩码
M1 = int('3'*64, 16)    # 4bit 掩码
M2 = int('0f'*32, 16)   # 8bit 掩码
K  = int('01'*32, 16)   # 收割乘数


cmd = (
    f"B=A>>1;B=B&{M0};A=A-B;"
    f"B=A>>2;B=B&{M1};A=A&{M1};A=A+B;"
    f"B=A>>4;B=B&{M2};A=A&{M2};A=A+B;"
    f"A=A*{K};"
    f"A=A>>248;"
)

'''
B=A>>1;B=B&M0;A=A-B;            (3步)  减法技巧：2bit字段 v−(v>>1)=popcount(v)
B=A>>2;B=B&M1;A=A&M1;A=A+B;     (4步)  折成 4bit 字段 ≤4
B=A>>4;B=B&M2;A=A&M2;A=A+B;     (4步)  折成 8bit 字段 ≤8
A=A*K;                          (3步)  K=00000001×32，32字节并行求和
A=A>>248;                       (1步)  结果落到低8位


'''
if __name__ == "__main__":

    STMT = re.compile(r"([AB])=([AB]|\d+)(\+|-|\*|//|<<|>>|&|\^|%)([AB]|\d+)")
    for i, s in enumerate(cmd[:-1].split(";")):
        print(i, repr(s[:50]), "OK" if STMT.fullmatch(s) else "← 坏")

    sock = socket.socket()
    sock.connect((ip, port))

    local_check(cmd)

    banner = recv_until(sock, b"> ")  # 等到提示符
    print(banner.decode("utf-8", errors="replace"))
    send_line(sock, cmd)
    out = recv_all(sock)  # 收 N / e / a_off / shift_bits / c_rsa / hill_ct


    print(out)



    sock.close()



