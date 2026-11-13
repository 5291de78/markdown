#!/usr/bin/env python3
"""MEV Relay replay service — Polygon searcher nonce-collision challenge.

Based on: Y. Madhwal et al., "Chain Reactions: How Nonce Collisions in ECDSA
Compromise Polygon MEV Searchers", arXiv:2605.21498 (2026), case C3
(cross-wallet nonce collisions).

Every connection replays a captured bundle of ECDSA signatures produced by
THREE searcher wallets that share a small pool of nonces.  The service hands
out the transcript and a *vault* signature made by one of the wallets, then
asks for that wallet's private key.  Nothing announces which wallet signed
which record, or how nonces are shared: the collision graph has to be
recovered from the data (collections of records with equal `r`, plus
consistency checks on the resulting linear system).

The transcript also contains decoy records signed by unrelated throw-away
keys, so "assume everything collides" does not work — those rows have to be
pruned by consistency.

This file is also shipped to players and stays runnable without the
production flag.
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

WALLETS = 3
SHARED_NONCES = 4
PRIVATE_NONCES = 1
DECOYS = 2
MAX_ATTEMPTS = 5
HANDLER_TIMEOUT = 900

FLAG = (os.environ.get("YL_DYFLAG") or os.environ.get("FLAG") or "YulinSec{local_only}").strip()
if not FLAG:
    raise RuntimeError("YL_DYFLAG/FLAG must not be empty")


def point_add(left, right):
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


def build_transcript():
    keys = [secrets.randbelow(ORDER - 1) + 1 for _ in range(WALLETS)]
    shared = [secrets.randbelow(ORDER - 1) + 1 for _ in range(SHARED_NONCES)]

    records = []
    counter = 0

    for wallet in range(WALLETS):
        for nonce in shared:
            message = f"polygon-auction::bid::{counter:03d}".encode()
            counter += 1
            z = message_z(message)
            r, s = sign(keys[wallet], z, nonce)
            if r and s:
                records.append((message, z, r, s))

    for wallet in range(WALLETS):
        for _ in range(PRIVATE_NONCES):
            nonce = secrets.randbelow(ORDER - 1) + 1
            message = f"polygon-auction::bid::{counter:03d}".encode()
            counter += 1
            z = message_z(message)
            r, s = sign(keys[wallet], z, nonce)
            if r and s:
                records.append((message, z, r, s))

    for _ in range(DECOYS):
        decoy_key = secrets.randbelow(ORDER - 1) + 1
        nonce = secrets.randbelow(ORDER - 1) + 1
        message = f"polygon-auction::noise::{counter:03d}".encode()
        counter += 1
        z = message_z(message)
        r, s = sign(decoy_key, z, nonce)
        if r and s:
            records.append((message, z, r, s))

    secrets.SystemRandom().shuffle(records)

    victim = secrets.randbelow(WALLETS)
    public_key = scalar_mul(keys[victim])

    vault_message = b"MEV-X vault :: withdraw :: escalate privileges"
    vault_z = message_z(vault_message)
    vault_nonce = secrets.randbelow(ORDER - 1) + 1
    vault_r, vault_s = sign(keys[victim], vault_z, vault_nonce)

    return keys[victim], public_key, records, (vault_message, vault_z, vault_r, vault_s)


class ChallengeHandler(socketserver.StreamRequestHandler):
    def send(self, text):
        self.wfile.write(text.encode("utf-8"))
        self.wfile.flush()

    def handle(self):
        self.request.settimeout(HANDLER_TIMEOUT)
        try:
            self.run_session()
        except (OSError, ValueError, OverflowError):
            return

    def run_session(self):
        private_key, public_key, records, vault = build_transcript()
        x, y = public_key

        self.send("MEV-X relay :: polygon bundle replay (read-only)\n")
        self.send("curve=secp256k1\n")
        self.send(f"captured_signatures={len(records)}\n")
        self.send(f"vault_wallet_pubkey=04{x:064x}{y:064x}\n")
        self.send(f"vault_wallet=searcher-{secrets.randbelow(900) + 100}\n")
        for index, (message, z, r, s) in enumerate(records):
            self.send(f"sig[{index}].message={message.decode('ascii')}\n")
            self.send(f"sig[{index}].hash={z:064x}\n")
            self.send(f"sig[{index}].r={r:064x}\n")
            self.send(f"sig[{index}].s={s:064x}\n")
        message, z, r, s = vault
        self.send(f"vault_op.message={message.decode('ascii')}\n")
        self.send(f"vault_op.hash={z:064x}\n")
        self.send(f"vault_op.r={r:064x}\n")
        self.send(f"vault_op.s={s:064x}\n")
        self.send("relay_sealed=1\n")

        for _ in range(MAX_ATTEMPTS):
            self.send("vault_private_key_hex> ")
            raw = self.rfile.readline(256)
            if not raw:
                return
            text = raw.decode("ascii", errors="ignore").strip().lower()
            while text.startswith("0x"):
                text = text[2:]
            try:
                submitted = int(text, 16) if text else None
            except ValueError:
                submitted = None
            if submitted is not None and submitted % ORDER == private_key:
                self.send(f"vault_credential={FLAG}\n")
                return
            self.send("rejected\n")
        self.wfile.flush()


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
