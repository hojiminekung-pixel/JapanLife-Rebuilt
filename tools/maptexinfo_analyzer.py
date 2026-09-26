#!/usr/bin/env python3
"""Inspect Japan Life 1.5.12 maptexinfo.smf without making speculative edits.

This tool intentionally treats 01 01 18 as a byte signature, not a record boundary.
The native library shows that the descriptor stream is variable-length.
"""

from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

MAPDATA_COUNT_BYTES = 4
SHA256_SIZE = 32
SIGNATURES = {
    "010118": bytes.fromhex("010118"),
    "01021e": bytes.fromhex("01021e"),
    "010124": bytes.fromhex("010124"),
    "020224": bytes.fromhex("020224"),
    "030324": bytes.fromhex("030324"),
    "040424": bytes.fromhex("040424"),
    "060624": bytes.fromhex("060624"),
}

def scan(path: Path) -> dict:
    data = path.read_bytes()
    if len(data) < 4:
        raise ValueError("maptexinfo is too small")

    count = int.from_bytes(data[:4], "little")
    hash_start = 4
    hash_end = hash_start + count * SHA256_SIZE

    if hash_end > len(data):
        raise ValueError("hash table exceeds file")

    hashes = [
        data[i:i + SHA256_SIZE].hex()
        for i in range(hash_start, hash_end, SHA256_SIZE)
    ]

    sigs = {}
    for name, sig in SIGNATURES.items():
        positions = []
        start = 0
        while True:
            p = data.find(sig, start)
            if p < 0:
                break
            positions.append(p)
            start = p + 1
        sigs[name] = {
            "count": len(positions),
            "first_offsets": positions[:20],
        }

    return {
        "file_size": len(data),
        "mapdata_count": count,
        "hash_table_offset": 4,
        "hash_table_bytes": count * SHA256_SIZE,
        "descriptor_stream_start": hash_end,
        "descriptor_stream_bytes": len(data) - hash_end,
        "signatures": sigs,
        "hashes": hashes,
    }

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("maptexinfo", type=Path)
    ap.add_argument("-o", "--output", type=Path)
    args = ap.parse_args()

    result = scan(args.maptexinfo)
    out = json.dumps(result, indent=2)
    if args.output:
        args.output.write_text(out + "\n", encoding="utf-8")
    else:
        print(out)

if __name__ == "__main__":
    main()
