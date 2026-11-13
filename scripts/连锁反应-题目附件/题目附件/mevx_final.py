# -*- coding: utf-8 -*-
"""Final solver for the MEV-X replay challenge (3 wallets x 4 shared nonces).

Structure (from shipped server source):
  3 wallets each sign with the SAME 4 shared nonces  -> 4 r-groups of 3 sigs
  + 1 private nonce per wallet (singleton) + 2 decoys (singleton).
  One of the 3 wallets is the vault. Each r-group = [vault, otherA, otherB],
  3 different keys sharing one nonce k.
  Per group, k-elimination gives 2 linear relations among (X0,X1,X2) — the
  wallet->slot assignment is unknown, so brute-force the labelings and keep
  the system that is consistent AND satisfies X0*G == vault pubkey.
"""
import itertools
import re
import socket
import sys

from ecdsa import SECP256k1, VerifyingKey

n = SECP256k1.order
G = SECP256k1.generator


def recv_until(sock, marker, timeout=30):
    sock.settimeout(timeout)
    buf = b''
    while marker not in buf:
        chunk = sock.recv(65536)
        if not chunk:
            break
        buf += chunk
    return buf


def solve_mod(rows, nvars):
    """Gaussian elimination mod n. rows: [coeffs..., rhs]. Returns solution
    list or None if inconsistent / underdetermined."""
    A = [r[:] for r in rows]
    A = [r for r in A if any(c % n for c in r[:nvars])]
    m = len(A)
    where = [-1] * nvars
    row = 0
    for c in range(nvars):
        piv = next((i for i in range(row, m) if A[i][c] % n), None)
        if piv is None:
            continue
        A[row], A[piv] = A[piv], A[row]
        inv = pow(A[row][c], -1, n)
        A[row] = [(v * inv) % n for v in A[row]]
        for i in range(m):
            if i != row and A[i][c] % n:
                f = A[i][c] % n
                A[i] = [(A[i][j] - f * A[row][j]) % n for j in range(nvars + 1)]
        where[c] = row
        row += 1
    for i in range(m):
        if all(A[i][c] % n == 0 for c in range(nvars)) and A[i][nvars] % n:
            return None                      # inconsistent
    if any(w == -1 for w in where):
        return None                          # underdetermined
    return [A[where[c]][nvars] for c in range(nvars)]


def verify(z, r, s, point):
    w = pow(s, -1, n)
    P = (z * w % n) * G + (r * w % n) * point
    return P.x() % n == r


def solve(host, port):
    sock = socket.create_connection((host, port), timeout=30)
    data = recv_until(sock, b'vault_private_key_hex> ').decode('ascii', 'replace')

    m = re.search(r'vault_wallet_pubkey=04([0-9a-f]{64})([0-9a-f]{64})', data)
    vault_point = VerifyingKey.from_string(bytes.fromhex(m.group(1) + m.group(2)),
                                           curve=SECP256k1).pubkey.point

    recs = {}
    for mm in re.finditer(r'sig\[(\d+)\]\.(hash|r|s)=([0-9a-f]{64})', data):
        recs.setdefault(int(mm.group(1)), {})[mm.group(2)] = int(mm.group(3), 16)
    sigs = {i: (d['hash'], d['r'], d['s']) for i, d in recs.items() if len(d) == 3}
    print(f"[*] parsed {len(sigs)} records")

    vault_idx = [i for i, (z, r, s) in sigs.items() if verify(z, r, s, vault_point)]
    print(f"[*] vault-signed records: {sorted(vault_idx)}")

    # group by r, keep multi-member groups (shared nonces)
    groups = {}
    for i, (z, r, s) in sigs.items():
        groups.setdefault(r, []).append(i)
    multi = [sorted(v) for r, v in groups.items() if len(v) >= 2]
    print(f"[*] {len(multi)} shared-nonce groups, sizes {[len(g) for g in multi]}")

    # per group: exactly 1 vault sig + 2 others -> build rows for each labeling
    group_rows = []
    for g in multi:
        vs = [i for i in g if i in vault_idx]
        os_ = [i for i in g if i not in vault_idx]
        if len(vs) != 1 or len(os_) != 2:
            print(f"[!] skipping odd group {g}")
            continue
        v, p, q = vs[0], os_[0], os_[1]
        zv, r, sv = sigs[v]
        zp, _, sp = sigs[p]
        zq, _, sq = sigs[q]
        variants = []
        for bit in (0, 1):
            # eq(v,p): sp*r*X0 - sv*r*Xp = sv*zp - sp*zv ; eq(v,q): likewise
            rows = [
                [sp * r % n, (-sv * r) % n, 0, (sv * zp - sp * zv) % n],
                [sq * r % n, 0, (-sv * r) % n, (sv * zq - sq * zv) % n],
            ]
            if bit:      # swap X1/X2 slots
                rows = [[r0[0], r0[2], r0[1], r0[3]] for r0 in rows]
            variants.append(rows)
        group_rows.append(variants)

    sol = None
    for combo in itertools.product((0, 1), repeat=len(group_rows)):
        rows = [r for g, bit in zip(group_rows, combo) for r in g[bit]]
        cand = solve_mod(rows, 3)
        if cand is None:
            continue
        P = cand[0] * G
        if P.x() == vault_point.x() and P.y() == vault_point.y():
            print(f"[+] consistent labeling {combo}")
            sol = cand
            break
    if sol is None:
        print("[-] no consistent solution")
        sock.close()
        return

    x0, x1, x2 = sol
    print(f"[+] wallet keys: vault={x0:064x}")
    print(f"                 other1={x1:064x}")
    print(f"                 other2={x2:064x}")
    for i, x in ((i, x1) for i in sigs if i not in vault_idx):
        pass  # (sanity of others optional)

    sock.sendall(f"{x0:064x}\n".encode())
    resp = sock.makefile().readline().strip()
    print(f"[<] {resp}")
    sock.close()


if __name__ == '__main__':
    host ="pwn.recruit.yulinsec.cn"
    port = 11077
    solve(host, port)
