#!/usr/bin/env python3
"""
Conservative Japan Life APK patcher.

The Thai fix is now a narrowly targeted data patch: the existing Font Pack 4
range begins at U+3130, while the same native renderer explicitly uses
FONTPACK_ID 4 for Thai layout handling. The original font.smf also contains
Thai glyph offsets (for example U+0E01).

The patch expands Pack 4's lower Unicode bound from U+3130 to U+0E00.
The upper bound U+32FF is preserved, so the original Korean/Jamo coverage
remains in the same pack.
"""

import argparse
import hashlib
import zipfile
from pathlib import Path

LIB = "lib/armeabi/libKyotoLife.so"

# Native font-pack metadata inside libKyotoLife.so:
#   pack 4 lower bound: U+3130
#   pack 4 upper bound: U+32FF
# This is in the file's .data section at this exact offset.
THAI_PACK4_LOWER_OFFSET = 0x2EFCF0
OLD_PACK4_LOWER = bytes.fromhex("30310000")  # U+3130
NEW_PACK4_LOWER = bytes.fromhex("000E0000")  # U+0E00

def sha256(data):
    return hashlib.sha256(data).hexdigest()

def patch_byte_range(data, offset, old, new):
    if data[offset:offset + len(old)] != old:
        raise RuntimeError(
            f"Precondition failed at 0x{offset:x}: "
            f"expected {old.hex()}, got {data[offset:offset + len(old)].hex()}"
        )
    out = bytearray(data)
    out[offset:offset + len(old)] = new
    return bytes(out)

def rebuild(src, dst, patched_lib):
    with zipfile.ZipFile(src, "r") as zin, zipfile.ZipFile(
        dst, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as zout:
        for info in zin.infolist():
            if info.filename.upper().startswith("META-INF/"):
                continue
            data = patched_lib if info.filename == LIB else zin.read(info.filename)
            zout.writestr(info, data)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("apk", type=Path)
    ap.add_argument("-o", "--output", type=Path, required=True)
    args = ap.parse_args()

    if not args.apk.is_file():
        raise SystemExit("APK not found")

    with zipfile.ZipFile(args.apk) as z:
        if LIB not in z.namelist():
            raise SystemExit(f"Missing required entry: {LIB}")
        original = z.read(LIB)

    patched = patch_byte_range(
        original,
        THAI_PACK4_LOWER_OFFSET,
        OLD_PACK4_LOWER,
        NEW_PACK4_LOWER,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    rebuild(args.apk, args.output, patched)

    with zipfile.ZipFile(args.output) as z:
        result = z.read(LIB)

    if result != patched:
        raise SystemExit("Postcondition failed: patched library differs")

    print("mode           : thai-pack4-range")
    print("original_sha256:", sha256(original))
    print("patched_sha256 :", sha256(patched))
    print("changed_offset :", hex(THAI_PACK4_LOWER_OFFSET))
    print("old_range_low  : U+3130")
    print("new_range_low  : U+0E00")
    print("range_high     : U+32FF")
    print("output         :", args.output)

if __name__ == "__main__":
    main()
