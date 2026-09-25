#!/usr/bin/env python3
import argparse, struct, zipfile, zlib

FONT = "res/raw/font.smf"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("apk")
    args = ap.parse_args()

    with zipfile.ZipFile(args.apk) as z:
        data = z.read(FONT)

    if data[:8] != b"nbc 0100":
        raise SystemExit(f"Unexpected font container header: {data[:8]!r}")

    raw = zlib.decompress(data[12:])
    if len(raw) < 8 + 65535 * 4:
        raise SystemExit("Font payload is too small for the native offset table")

    count, font_size = struct.unpack_from("<II", raw, 0)
    table_base = 8

    mapped = []
    for cp in range(0x0E00, 0x0E80):
        off = struct.unpack_from("<I", raw, table_base + cp * 4)[0]
        if off:
            mapped.append((cp, off))

    print("font_count:", count)
    print("font_size :", font_size)
    print("thai_mapped:", len(mapped), "/ 128")
    print("first:", [(f"U+{cp:04X}", hex(off)) for cp, off in mapped[:10]])
    print("last :", [(f"U+{cp:04X}", hex(off)) for cp, off in mapped[-10:]])

    if len(mapped) == 0:
        raise SystemExit("No Thai glyph records found")

if __name__ == "__main__":
    main()
