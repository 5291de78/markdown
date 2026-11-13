#!/usr/bin/env python3
"""AffineVault cold-signer service.

The vault signs two audit records with ECDSA nonces taken from an affine
ladder:

    k1 <- random
    k2 <- a * k1 + b  (mod n)

The ladder coefficients are expanded from a 16-bit trim register.  The
register value is secret, but the expansion and the bit width are public, so
only 2^16 candidate ladders exist.  This file is also shipped to players as
the challenge attachment and stays runnable without the production flag.
"""

from __future__ import annotations

import hashlib
import os
import secrets
import socketserver

FIELD = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
GX = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
GY = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
GENERATOR = (GX, GY)

MESSAGES = (
    b"YulinSec cold vault audit :: 2026-Q1 deposit",
    b"YulinSec cold vault audit :: 2026-Q1 withdraw",
)
TRIM_BITS = 16
MAX_ATTEMPTS = 5
HANDLER_TIMEOUT = 600

FLAG = (os.environ.get("YL_DYFLAG") or os.environ.get("FLAG") or "YulinSec{local_only}").strip()
if not FLAG:
    raise RuntimeError("YL_DYFLAG/FLAG must not be empty")


def point_add(left, right):
    """Add two affine points; None is the point at infinity."""
    if left is None:
        return right
    if right is None:
        return left

    x1, y1 = left
    x2, y2 = right
    if x1 == x2:
        if (y1 + y2) % FIELD == 0:
            return None
        slope = 3 * x1 * x1 * pow(2 * y1, -1, FIELD) % FIELD
    else:
        slope = (y2 - y1) * pow(x2 - x1, -1, FIELD) % FIELD

    x3 = (slope * slope - x1 - x2) % FIELD
    return x3, (slope * (x1 - x3) - y1) % FIELD


def scalar_mul(k, point=GENERATOR):
    result = None
    while k:
        if k & 1:
            result = point_add(result, point)
        point = point_add(point, point)
        k >>= 1
    return result


def message_z(message):
    return int.from_bytes(hashlib.sha256(message).digest(), "big") % ORDER


def sign(private_key, z, nonce):
    r = scalar_mul(nonce)[0] % ORDER
    s = pow(nonce, -1, ORDER) * (z + r * private_key) % ORDER
    return r, s


def ladder_from_trim(trim):
    multiplier = 2 + (trim >> 11)
    offset = trim & 0x7FF
    return multiplier, offset


def build_transcript():
    private_key = secrets.randbelow(ORDER - 1) + 1
    public_key = scalar_mul(private_key)

    trim = secrets.randbelow(1 << TRIM_BITS)
    multiplier, offset = ladder_from_trim(trim)
    while True:
        k1 = secrets.randbelow(ORDER - 1) + 1
        k2 = (multiplier * k1 + offset) % ORDER
        if k2 == 0:
            continue
        records = []
        for message, nonce in zip(MESSAGES, (k1, k2)):
            z = message_z(message)
            r, s = sign(private_key, z, nonce)
            if r and s:
                records.append((message, z, r, s))
        if len(records) == 2:
            break

    return private_key, public_key, records


class ChallengeHandler(socketserver.StreamRequestHandler):
    def send(self, text):
        self.wfile.write(text.encode("utf-8"))
        self.wfile.flush()

    def handle(self):
        self.request.settimeout(HANDLER_TIMEOUT)
        try:
            self.run_session()
        except (OSError, ValueError):
            return

    def run_session(self):
        private_key, public_key, records = build_transcript()
        x, y = public_key

        self.send("AffineVault cold-signer v1.2 (audit mode)\n")
        self.send("curve=secp256k1\n")
        self.send(f"pubkey=04{x:064x}{y:064x}\n")
        for index, (message, z, r, s) in enumerate(records):
            self.send(f"record[{index}].message={message.decode('ascii')}\n")
            self.send(f"record[{index}].hash={z:064x}\n")
            self.send(f"record[{index}].r={r:064x}\n")
            self.send(f"record[{index}].s={s:064x}\n")
        self.send("nonce_ladder=affine-trim16\n")
        self.send("vault_sealed=1\n")

        for attempt in range(1, MAX_ATTEMPTS + 1):
            self.send("private_key_hex> ")
            raw = self.rfile.readline(256)
            if not raw:
                return

            text = raw.decode("ascii", errors="ignore").strip().lower()
            if text.startswith("0x"):
                text = text[2:]
            try:
                submitted = int(text, 16)
            except ValueError:
                submitted = None

            if submitted is not None and submitted == private_key:
                self.send(f"audit_token={FLAG}\n")
                return
            self.send(f"invalid private key ({attempt}/{MAX_ATTEMPTS})\n")

        self.send("vault locked.\n")


class ChallengeServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True
    request_queue_size = 64


def main():
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "20000"))
    with ChallengeServer((host, port), ChallengeHandler) as server:
        server.serve_forever()


if __name__ == "__main__":
    main()
