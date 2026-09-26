#!/usr/bin/env python3
"""Analyze Japan Life object -> EMAPTEX -> mapdata resource links.

This is a diagnostic tool only. It never modifies the APK.
It targets the verified 1.5.12 resource format:
  data_building.smf -> object record -> EMAPTEX
  EMAPTEX / 20 -> mapdataNNN
  EMAPTEX % 20 -> texture slot inside that mapdata resource.

The tool also detects the common 2x2 PNG placeholder payload used by
missing/late-content mapdata resources.
"""

from __future__ import annotations

import argparse
import json
import struct
import zlib
from pathlib import Path


def nbc_decompress(path: Path) -> bytes:
    raw = path.read_bytes()
    if raw[:8] != b"nbc 0100":
        raise ValueError(f"{path.name}: unsupported/missing NBC header")
    return zlib.decompress(raw[12:])


def parse_buildings(path: Path):
    data = nbc_decompress(path)
    marker = b"\x01\x00\x01\x00"
    out = []
    pos = 0

    while True:
        pos = data.find(marker, pos)
        if pos < 0 or pos + 8 > len(data):
            break

        object_id = struct.unpack_from("<H", data, pos + 4)[0]
        name_len = struct.unpack_from("<H", data, pos + 6)[0]
        if not 1 <= name_len <= 120 or pos + 8 + name_len > len(data):
            pos += 4
            continue

        name = data[pos + 8:pos + 8 + name_len].split(b"\0", 1)[0]
        try:
            name = name.decode("ascii")
        except UnicodeDecodeError:
            pos += 4
            continue

        after_name = pos + 8 + name_len
        if after_name + 8 <= len(data):
            emaptex = struct.unpack_from("<I", data, after_name + 4)[0]
            out.append(
                {
                    "object_id": object_id,
                    "name": name,
                    "offset": pos + 8,
                    "emaptex": emaptex,
                    "mapdata": emaptex // 20,
                    "slot": emaptex % 20,
                }
            )
        pos += 4

    return out


def classify_mapdata(path: Path) -> dict:
    raw = path.read_bytes()
    if raw[:8] != b"nbc 0100":
        return {"format": "raw", "size": len(raw)}

    data = zlib.decompress(raw[12:])
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        # A mapdata resource can contain multiple concatenated PNGs.
        starts = []
        p = 0
        while True:
            p = data.find(b"\x89PNG\r\n\x1a\n", p)
            if p < 0:
                break
            starts.append(p)
            p += 8

        # The base late-content placeholder consists of 20 identical 2x2 PNGs.
        return {
            "format": "concatenated_png",
            "decompressed_size": len(data),
            "png_count": len(starts),
            "first_png_size": (
                int.from_bytes(data[16:20], "big"),
                int.from_bytes(data[20:24], "big"),
            ) if len(data) >= 24 else None,
            "is_2x2_placeholder_set": len(starts) == 20
            and all(
                len(data[s:s + 32]) >= 24
                and int.from_bytes(data[s + 16:s + 20], "big") == 2
                and int.from_bytes(data[s + 20:s + 24], "big") == 2
                for s in starts
            ),
        }

    return {
        "format": "nested_nbc_or_binary",
        "decompressed_size": len(data),
        "prefix": data[:16].hex(),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("apk_res_raw", type=Path, help="Extracted APK res/raw directory")
    ap.add_argument("--object", action="append", type=int, dest="objects")
    ap.add_argument("--contains", default=None)
    args = ap.parse_args()

    raw = args.apk_res_raw
    buildings = parse_buildings(raw / "data_building.smf")
    if args.objects:
        buildings = [x for x in buildings if x["object_id"] in args.objects]
    if args.contains:
        needle = args.contains.upper()
        buildings = [x for x in buildings if needle in x["name"].upper()]

    for row in buildings:
        p = raw / f"mapdata{row['mapdata']:03d}.smf"
        row["mapdata_present"] = p.exists()
        row["mapdata_info"] = classify_mapdata(p) if p.exists() else None

    print(json.dumps({
        "count": len(buildings),
        "objects": buildings,
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
