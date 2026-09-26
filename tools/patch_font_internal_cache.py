#!/usr/bin/env python3
"""Force Japan Life generic cache/save files onto the app-internal FileManager path.

The original client asks JNI_CheckExternalStorage() whether external storage is
available. On modern Android this can report available while the legacy external
file path still cannot be created/read. Generic font-cache creation then fails
without an internal fallback. This patch makes the compatibility layer choose
the existing internal path for generic files.

Only the exact v1.5.12 native function is patched:
CFontRenderer's callers reach CSaveDataManager::IsExternalStorageAvailable().
"""
from __future__ import annotations
import argparse, hashlib, zipfile
from pathlib import Path

ORIGINAL_NATIVE_SHA256 = "0d82ff380548030163eb46be396d672ddb41832f8307680d2a1b14faaf9b3b1f"
OFFSET = 0x133CB4
OLD = bytes.fromhex("10 b5 25 f1 ea fe ab a9")
NEW = bytes.fromhex("00 20 70 47 ab fe 00 06")

def patch_native(lib: bytes) -> bytes:
    got=hashlib.sha256(lib).hexdigest()
    if got != ORIGINAL_NATIVE_SHA256:
        raise SystemExit(f"unexpected libKyotoLife.so sha256: {got}")
    if lib[OFFSET:OFFSET+8] != OLD:
        raise SystemExit(f"unexpected bytes at 0x{OFFSET:x}: {lib[OFFSET:OFFSET+8].hex()}")
    out=bytearray(lib)
    out[OFFSET:OFFSET+8]=NEW
    return bytes(out)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("apk",type=Path)
    ap.add_argument("-o","--output",type=Path,required=True)
    args=ap.parse_args()
    with zipfile.ZipFile(args.apk,"r") as zin:
        names=zin.namelist()
        lib=zin.read("lib/armeabi/libKyotoLife.so")
        patched=patch_native(lib)
        with zipfile.ZipFile(args.output,"w") as zout:
            for info in zin.infolist():
                data=patched if info.filename=="lib/armeabi/libKyotoLife.so" else zin.read(info.filename)
                zout.writestr(info,data)
    print("original_native_sha256",hashlib.sha256(lib).hexdigest())
    print("patched_native_sha256",hashlib.sha256(patched).hexdigest())
    print("patched_offset",hex(OFFSET))
    print("output",args.output)
if __name__=="__main__":
    main()
