'''
ip = '127.0.0.1'
port = 20000

import socket
sock = socket.socket()
sock.connect((ip, port))

sock.sendall('send_context'.encode())		# 向 server 发送一些内容
recieve_context = sock.recv(1024).decode()	# 从 server 读取一些内容
nc pwn.recruit.yulinsec.cn 11037
'''

import socket
from ftplib import all_errors

if input('next>') == '0':
    ip = 'pwn.recruit.yulinsec.cn'
    port = 11037
elif input('next>') == '1':
    ip = '127.0.0.1'
    port = 20000
else:
    all_errors
sock = socket.socket()
sock.connect((ip, port))

while 1:
    cmd = input('cmd>')
    if not cmd:
        recieve = sock.recv(1024).decode()
        print(recieve)
        print("="*40)
    else:
        cmd += '\n'
        sock.sendall(cmd.encode())
        recieve = sock.recv(1024).decode()
        print(f"send{cmd}")
        print("="*40)
        print(recieve)
        print("="*40)


print(recieve)
sock.close()