#!/usr/bin/env python3
"""Convert Japan Life 1.5.12 packaged maptexinfo.smf to native runtime form."""
from __future__ import annotations
import argparse, json, struct, zlib
from pathlib import Path

HEADER = 7524
SLOTS = 4685

def legacy_records(src: bytes):
    pos = HEADER
    rows = []
    while pos < len(src):
        if pos + 3 > len(src):
            raise ValueError(f"short record header at 0x{pos:x}")
        n = src[pos + 2]
        size = 7 + 4 * n
        if pos + size > len(src):
            raise ValueError(f"record exceeds file at 0x{pos:x}")
        payload = struct.unpack_from("<I", src, pos + 3 + 4 * n)[0]
        rows.append((pos, n, size, payload))
        pos += size
    if len(rows) != SLOTS or pos != len(src):
        raise ValueError(f"expected {SLOTS} records, got {len(rows)}; end={pos}")
    return rows

def mapdata_chunk_offsets(directory: Path):
    result = []
    for i in range(235):
        b = (directory / f"mapdata{i:03d}.smf").read_bytes()
        d = zlib.decompress(b[12:])
        pos, offsets = 0, []
        while pos < len(d):
            if d[pos:pos+4] == b"\x89PNG":
                end = d.find(b"IEND", pos)
                if end < 0:
                    raise ValueError(f"PNG without IEND in mapdata{i:03d}")
                offsets.append(pos)
                pos = end + 8
                continue
            if pos + 16 <= len(d):
                typ, size = struct.unpack_from("<II", d, pos)
                if typ == 2 and pos + 8 + size <= len(d) and d[pos+8:pos+16] == b"nbc 0100":
                    offsets.append(pos)
                    pos += 8 + size
                    continue
            raise ValueError(f"unknown chunk at mapdata{i:03d}+0x{pos:x}")
        result.append(offsets)
    return result

def convert(src_path: Path, dst_path: Path, mapdata_dir: Path | None):
    src = src_path.read_bytes()
    rows = legacy_records(src)
    expected = mapdata_chunk_offsets(mapdata_dir) if mapdata_dir else None
    out = bytearray(src[:HEADER])
    mismatches = []
    for slot, (pos, n, size, payload) in enumerate(rows):
        # Legacy records contain a second half of coordinate bytes that the
        # 1.5.12 native loader does not consume. Keep the first half only.
        out += src[pos:pos+3]
        out += src[pos+3:pos+3 + 2*n]
        out += src[pos+3 + 4*n:pos+7 + 4*n]
        if expected is not None:
            mi, ci = slot // 20, slot % 20
            want = expected[mi][ci] if ci < len(expected[mi]) else None
            if payload != want:
                mismatches.append((slot, mi, ci, payload, want))
    if mismatches:
        raise ValueError(f"payload mismatches: {mismatches[:3]}")
    dst_path.write_bytes(out)
    return {
        "source_size": len(src),
        "output_size": len(out),
        "records": len(rows),
        "descriptor_start": HEADER,
        "legacy_descriptor_bytes": len(src) - HEADER,
        "native_descriptor_bytes": len(out) - HEADER,
        "offset_mismatches": len(mismatches),
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("output")
    ap.add_argument("--mapdata-dir")
    ap.add_argument("--report")
    a = ap.parse_args()
    report = convert(
        Path(a.source),
        Path(a.output),
        Path(a.mapdata_dir) if a.mapdata_dir else None,
    )
    print(json.dumps(report, indent=2))
    if a.report:
        Path(a.report).write_text(json.dumps(report, indent=2), encoding="utf-8")

if __name__ == "__main__":
    main()
