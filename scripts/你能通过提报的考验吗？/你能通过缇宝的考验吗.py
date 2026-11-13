#https://blog.csdn.net/weixin_44110537/article/details/108956759
#https://ce-automne.github.io/2020/02/16/RSA-LSB-Oracle%E6%94%BB%E5%87%BB%E5%8E%9F%E7%90%86%E5%88%86%E6%9E%90/
'''
==================== 一线天机 ====================
白厄穿过旋门，踏入天机圣所。缇宝捧着一卷无字的谶语，
赛飞儿坐在门槛上，慢悠悠地晃着一串不知真假的钥匙。

缇宝：「火种之印已封入谶语。天机万卷，只露一线。」
coreflame=1165c7448651807a84b9f28154e994efb6fb1fbc7fd774a4d6c6bed34691040b365923758c9fa5a4d93b41c24265a2e4c6e18d337077927a23ef59b7c61ad0c6c2a1b64d57a368f620d1aff6f704564965f44d4b8c7e65c56f4eda6b86c9133d20939c7a4a9e9a00d0c44be4870561010b4129024d82b07848af33c59063f800b0b5f8b4b3cfdb778b16e19bc2663e3e023d7421a9b5cd748485ed593ae57fa85d59390816c0afe0bfa9ba68ff5071d6f43aeae7e5105b8e997f79c5e85ba45e5377deab989da7d5c9dbf86025a9e821cf2d0dc090a08647533959de58063df7850bc90586c100ea0e254a6a63a633553750111c7cab49bab44b230f5267c49f
赛飞儿：「想求签？本小姐的戏法一场只演 8 次。
        想问天机？缇宝最多奉陪 2100 次，问完谶语就自己合上。
        哦，提示只有一个——我偷走的那枚指数，
        九位往上，十六位封顶。」

指令：divine [m_hex] | omen [c_hex] | leave
> omen=1
omen_left=2099
>

进程已结束，退出代码为 0
'''
import socket
import math
import re
# 256 * 8 = 2048

from binascii import a2b_hex
import decimal
from Crypto.Util.number import *

ip = "pwn.recruit.yulinsec.cn"
port = 11057
pat0 = re.compile(r'cipher=([0-9a-fA-F]+)')
pat1 = re.compile(r'> omen=([0-9a-fA-F]+)')

def lsbOracle(c):
    r.recv()
    r.sendline("2")
    r.recvuntil("c = ")
    r.sendline(str(c))
    m = r.recvline().strip()[3:]
    print("m: " + m)
    m = int(m)
    return m


def revealFlag(c, n):
    k = n.bit_length()  # 二进制长度数，这里是1024
    decimal.getcontext().prec = k  # 设定小数点精度
    low = decimal.Decimal(0)
    high = decimal.Decimal(n)
    for i in range(k):
        plaintext = (low + high) / 2
        state = lsbOracle(c)
        if not state:  # state = 0
            high = plaintext  # 0<high<n/2
        else:
            low = plaintext
        c = (c * pow(2, e, n)) % n
        print
        i, state, int(high - low)
    return int(high)


def send_line(sock,msg:str):
    msg = str(msg)
    sock.sendall((msg + '\n').encode("utf-8"))




def recv_all(sock, timeout=1):
    buf = b""
    sock.settimeout(timeout)
    try:
        while True:
            chunk = sock.recv(1024)
            if not chunk:
                break
            buf += chunk
    except socket.timeout:
        pass
    sock.settimeout(None)
    return buf.decode("utf-8", errors="replace")

def oracle(m):
    send_line(sock, m)
    resp0 = recv_all(sock)
    print("RAW_RESP:", repr(resp0))          # 调试：看服务端到底返回什么
    mm = pat1.search(resp0)                  # search 从任意位置找，match 只从开头找
    if mm is None:
        raise ValueError("回包里没有 'omen='，原文：%r" % resp0)
    return int(mm.group(1), 16)
# 使用



if __name__ == '__main__':
    sock = socket.socket()
    sock.connect((ip, port))
    resp = recv_all(sock)
    print(resp)
    c_list = [0] * 6
    for i in range(6):
        c_list[i] = oracle(2 ** i)
        print("c" + str(i) + "=" + str(c_list[i]))
    n = c_list[0]
    for i in range(1, 6):
        n = math.gcd(n, c_list[i])
        print("gcd>", n)
    while True:
        s = input("next>")
        if s == "s":
            send_line(sock,input("send>"))
            print(recv_all(sock))



    sock.close()

    '''
    e = 65537
    r.recv()
    r.sendline("1")
    c = r.recvline().strip()[3:]
    print("c: " + c)
    c = int(c)
    n = r.recvline().strip()[3:]
    print("n: " + n)
    n = int(n)
    res = revealFlag((c * pow(2, e, n)) % n, n)
    # res = 1624569960321307593137113337496607296102769342145048575242
    print
    res
    res_hex = hex(res)
    # print res_hex
    print
    a2b_hex(res_hex[2:])  # 一种方式打印flag
    print
    long_to_bytes(res)  # 另一种方式打印flag
    '''

