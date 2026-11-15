#!/usr/bin/env python3

from __future__ import annotations

import os
import secrets
import socketserver


FLAG = os.environ.get("YL_DYFLAG") or os.environ.get("FLAG") or "YulinSec{local_only}"
FLAG = FLAG.strip()
if not FLAG:
    raise RuntimeError("YL_DYFLAG/FLAG must not be empty")
KEY = FLAG.encode("utf-8")


def encrypt(pt: bytes) -> bytes:
    r = secrets.randbelow(len(KEY))
    prev = 0
    ct = bytearray()
    for i, value in enumerate(pt):
        current = value ^ prev ^ KEY[(i + r) % len(KEY)]
        ct.append(current)
        prev = current
    return bytes(ct)


class Handler(socketserver.StreamRequestHandler):
    def send_line(self, value: str) -> None:
        self.wfile.write(value.encode() + b"\n")
        self.wfile.flush()

    def handle(self) -> None:
        self.wfile.write(b"> ")
        self.wfile.flush()
        while True:
            raw = self.rfile.readline()
            if not raw:
                return
            text = raw.rstrip(b"\r\n").decode("utf-8", errors="replace")
            if not 1 <= len(text) <= 4:
                self.send_line("ERROR: text length must be between 1 and 4.")
                return
            if not all("A" <= char <= "Z" for char in text):
                self.send_line("ERROR: input context unavailable.")
                return
            self.send_line(f"cipher={encrypt(text.encode('ascii')).hex()}")
            self.wfile.write(b"> ")
            self.wfile.flush()


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "20000"))
    with Server((host, port), Handler) as server:
        server.serve_forever()
