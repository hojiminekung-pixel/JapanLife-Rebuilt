#!/usr/bin/env python3
"""
Conservative Japan Life APK patcher.

The production Thai fix is intentionally not enabled yet. The historical
fallback experiment is retained only as a reproducible test, and a second
test forces the existing language-selection fallback to FONTPACK_ID 4, the
Thai pack described by the native font-pack metadata.
"""

import argparse, hashlib, zipfile
from pathlib import Path

LIB = "lib/armeabi/libKyotoLife.so"

# DetermineLanguage() contains:
#   movs r3, #1
#   rsbs r0, r3, #0
# at virtual/file offset 0x14db0e for the immediate byte.
# Replacing that immediate changes the fallback language.
FALLBACK_IMMEDIATE_OFFSET = 0x14DB0E

def sha256(data):
    return hashlib.sha256(data).hexdigest()

def patch_byte(data, offset, old, new):
    if data[offset] != old:
        raise RuntimeError(
            f"Precondition failed at 0x{offset:x}: "
            f"expected {old:#x}, got {data[offset]:#x}"
        )
    out = bytearray(data)
    out[offset] = new
    return bytes(out)

def rebuild(src, dst, patched_lib):
    with zipfile.ZipFile(src, "r") as zin, zipfile.ZipFile(
        dst, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as zout:
        for info in zin.infolist():
            if info.filename.upper().startswith("META-INF/"):
                # Old signatures/digests are invalid after modification.
                continue
            data = patched_lib if info.filename == LIB else zin.read(info.filename)
            zout.writestr(info, data)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("apk", type=Path)
    ap.add_argument("-o", "--output", type=Path, required=True)
    ap.add_argument("--experimental-fallback", action="store_true",
                    help="Reproduce the old fallback-to-pack-0 experiment.")
    ap.add_argument("--thai-pack4-test", action="store_true",
                    help="Test fallback-to-FONTPACK_ID-4 (Thai).")
    args = ap.parse_args()

    if args.experimental_fallback == args.thai_pack4_test:
        raise SystemExit("Choose exactly one experimental patch mode.")

    with zipfile.ZipFile(args.apk) as z:
        if LIB not in z.namelist():
            raise SystemExit(f"Missing required entry: {LIB}")
        original = z.read(LIB)

    if args.experimental_fallback:
        # Historical test: fallback 1 -> 0.
        patched = patch_byte(
            original, FALLBACK_IMMEDIATE_OFFSET, 0x01, 0x00
        )
        label = "fallback-0"
    else:
        # Newer targeted test: unsupported-language fallback -> Thai pack 4.
        patched = patch_byte(
            original, FALLBACK_IMMEDIATE_OFFSET, 0x01, 0x04
        )
        label = "fallback-thai-pack4"

    args.output.parent.mkdir(parents=True, exist_ok=True)
    rebuild(args.apk, args.output, patched)

    with zipfile.ZipFile(args.output) as z:
        result = z.read(LIB)
    if result != patched:
        raise SystemExit("Postcondition failed: patched library differs")

    print("mode           :", label)
    print("original_sha256:", sha256(original))
    print("patched_sha256 :", sha256(patched))
    print("changed_offset :", hex(FALLBACK_IMMEDIATE_OFFSET))
    print("output         :", args.output)

if __name__ == "__main__":
    main()
