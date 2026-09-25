#!/usr/bin/env python3
"""
Conservative Japan Life APK patcher.

This tool deliberately refuses to patch unknown APKs. Every native patch has
an exact expected byte sequence and replacement sequence. The current Thai
fallback experiment is disabled by default because it did not solve the
visible square-glyph problem.

Use --experimental-fallback only when reproducing that historical test.
"""

import argparse, hashlib, shutil, tempfile, zipfile
from pathlib import Path

LIB = "lib/armeabi/libKyotoLife.so"

# Historical experiment only. Offset is zero-based.
EXPERIMENTAL = {
    1_366_798: (b"\x01", b"\x00"),
}

def sha256(data):
    return hashlib.sha256(data).hexdigest()

def patch_one(data, offset, old, new):
    if data[offset:offset+len(old)] != old:
        raise RuntimeError(
            f"Precondition failed at 0x{offset:x}: "
            f"expected {old.hex()}, got {data[offset:offset+len(old)].hex()}"
        )
    return data[:offset] + new + data[offset+len(old):]

def rebuild(src, dst, patched_lib):
    with zipfile.ZipFile(src, "r") as zin, zipfile.ZipFile(
        dst, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as zout:
        for info in zin.infolist():
            if info.filename == LIB:
                zout.writestr(info, patched_lib)
            elif info.filename.upper().startswith("META-INF/"):
                # Old signatures/digests are invalid after modification.
                continue
            else:
                zout.writestr(info, zin.read(info.filename))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("apk", type=Path)
    ap.add_argument("-o", "--output", type=Path, required=True)
    ap.add_argument("--experimental-fallback", action="store_true")
    args = ap.parse_args()

    if not args.apk.is_file():
        raise SystemExit("APK not found")

    with zipfile.ZipFile(args.apk) as z:
        if LIB not in z.namelist():
            raise SystemExit(f"Missing required entry: {LIB}")
        original = z.read(LIB)

    patched = original
    changes = []

    if args.experimental_fallback:
        for offset, (old, new) in EXPERIMENTAL.items():
            patched = patch_one(patched, offset, old, new)
            changes.append({
                "offset": hex(offset),
                "old": old.hex(),
                "new": new.hex(),
            })
    else:
        raise SystemExit(
            "No production patch is enabled yet. "
            "The previous fallback experiment is known not to fix Thai squares."
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    rebuild(args.apk, args.output, patched)

    # Verify the patched library is exactly what was requested.
    with zipfile.ZipFile(args.output) as z:
        result = z.read(LIB)

    if result != patched:
        raise SystemExit("Postcondition failed: patched library differs")

    print("original_sha256:", sha256(original))
    print("patched_sha256 :", sha256(patched))
    print("changes:", changes)
    print("output:", args.output)

if __name__ == "__main__":
    main()
