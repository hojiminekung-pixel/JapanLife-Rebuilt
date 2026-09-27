#!/usr/bin/env python3
"""Audit World Life mapdata containers without modifying them.

Usage:
  python3 tools/audit_mapdata.py /path/to/extracted-apk/res/raw
"""
from pathlib import Path
import sys, zlib, hashlib

try:
    from PIL import Image
except ImportError:
    Image = None

root=Path(sys.argv[1]) if len(sys.argv)>1 else Path("res/raw")
rows=[]
for i in range(235):
    p=root/f"mapdata{i:03d}.smf"
    if not p.exists():
        rows.append((i,"MISSING",0,""))
        continue
    b=p.read_bytes()
    kind="other"
    detail=""
    if b[:8]==b"nbc 0100":
        try:
            d=zlib.decompress(b[12:])
            kind="nbc"
            if d.startswith(b"\x89PNG") and Image:
                from io import BytesIO
                im=Image.open(BytesIO(d)).convert("RGBA")
                if im.getbbox() is None:
                    kind="transparent-2x2-placeholder" if im.size==(2,2) else "transparent-png"
                detail=f"{im.width}x{im.height}"
            else:
                detail=f"decompressed={len(d)}"
        except Exception as e:
            kind="nbc-decompression-error"; detail=str(e)
    rows.append((i,kind,len(b),detail))

for r in rows:
    print(f"{r[0]:03d}\t{r[1]:32}\t{r[2]:8}\t{r[3]}")
print("\nplaceholder count:", sum(r[1]=="transparent-2x2-placeholder" for r in rows))
print("missing count:", sum(r[1]=="MISSING" for r in rows))
