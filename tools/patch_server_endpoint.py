#!/usr/bin/env python3
"""Patch the original Japan Life API base URL.

Usage:
  python tools/patch_server_endpoint.py input.apk output.apk --server http://192.168.1.100:8080

The replacement must fit in the existing native string slot. The original
client endpoint is https://japanlife.nubee.com/json/.
"""
from __future__ import annotations
import argparse, shutil, tempfile, zipfile
from pathlib import Path

OLD = b"https://japanlife.nubee.com/json/"
LIB = "lib/armeabi/libKyotoLife.so"

def patch_lib(data: bytes, new_base: str) -> bytes:
    old = OLD
    new = new_base.rstrip("/").encode() + b"/"
    if len(new) > len(old):
        raise SystemExit(f"new endpoint is too long: {len(new)} > {len(old)} bytes")
    hits = data.count(old)
    if hits != 1:
        raise SystemExit(f"expected exactly one API base string, found {hits}")
    padded = new + b"\0" * (len(old) - len(new))
    return data.replace(old, padded)

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("input_apk", type=Path)
    ap.add_argument("output_apk", type=Path)
    ap.add_argument("--server", required=True)
    args = ap.parse_args()

    with zipfile.ZipFile(args.input_apk, "r") as zin, zipfile.ZipFile(args.output_apk, "w") as zout:
        for info in zin.infolist():
            payload = zin.read(info.filename)
            if info.filename == LIB:
                payload = patch_lib(payload, args.server)
            zout.writestr(info, payload)

if __name__ == "__main__":
    main()
