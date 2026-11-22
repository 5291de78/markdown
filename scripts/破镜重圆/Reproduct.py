import socket


def recv_until(sock: socket.socket, marker: bytes) -> bytes:
    """持续接收，直到收到指定的结束标记或连接关闭。"""
    data = bytearray()

    while not data.endswith(marker):
        chunk = sock.recv(1024)
        if not chunk:
            break
        data.extend(chunk)

    return bytes(data)


def sock_recv(ip="127.0.0.1", port=20000, timeout=None):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        sock.connect((ip, port))

        while True:
            # 接收服务端响应，包括下一次输入提示符 "> "
            data = recv_until(sock, b"> ")
            if data:
                print(
                    data.decode("utf-8", errors="replace"),
                    end="",
                    flush=True,
                )

            # 数据不以提示符结尾，说明服务端已经关闭连接
            if not data.endswith(b"> "):
                print("\n[-] 服务端已关闭连接")
                break

            # 输入必须放在循环内部，每轮重新读取
            while True:
                try:
                    message = input()
                except (EOFError, KeyboardInterrupt):
                    print("\n[*] 客户端退出")
                    return

                if message:
                    break

                # 忽略空输入，并重新显示提示符
                print("> ", end="", flush=True)

            sock.sendall(message.encode("utf-8") + b"\n")


def main():
    sock_recv()


if __name__ == "__main__":
    main()
