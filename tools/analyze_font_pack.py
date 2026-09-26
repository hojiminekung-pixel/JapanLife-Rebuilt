#!/usr/bin/env python3
"""Analyze Japan Life 1.5.12 font-pack metadata and Thai glyph coverage."""
from __future__ import annotations
import argparse, json, struct, zipfile, zlib
from pathlib import Path

LIB="lib/armeabi/libKyotoLife.so"
FONT="res/raw/font.smf"
PACK_TABLE=0x2ef4ac
PACKS=[
    (0, 0x2ef4a4),
    (1, 0x2ef6b8),
    (2, 0x2ef8cc),
    (3, 0x2efadc),
    (4, 0x2efefc),
]
def u32(b,o): return struct.unpack_from("<I",b,o)[0]
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("apk",type=Path); ap.add_argument("-o","--output",type=Path)
    a=ap.parse_args()
    with zipfile.ZipFile(a.apk) as z:
        lib=z.read(LIB); fd=z.read(FONT)
    raw=zlib.decompress(fd[12:])
    count,font_size=struct.unpack_from("<II",raw,0)
    thai=[]
    for cp in range(0x0e00,0x0e80):
        off=struct.unpack_from("<I",raw,8+cp*4)[0]
        if off:
            end=struct.unpack_from("<I",raw,8+(cp+1)*4)[0] if cp<0xffff else 0
            thai.append({"codepoint":f"U+{cp:04X}","offset":off,"next_offset":end,"record_size":end-off if end>off else None})
    packs=[]
    for pid,addr in PACKS:
        ranges=u32(lib,addr-8) if False else None
    # The native pack descriptors are in .data at the fixed addresses below.
    for pid,addr in PACKS:
        # addr points at the range-count field for packs 1..4; pack0 is legacy.
        packs.append({"id":pid,"descriptor_address":hex(addr)})
    # Verified pack 4 descriptor: id=4, range_count=2, primary Thai range U+0E00..U+0E7F,
    # followed by 0xffffffff sentinel. The second count slot is not another Unicode range.
    p4=0x2efefc
    report={
        "font_header":{"count":count,"font_size":font_size,"raw_size":len(raw)},
        "pack4":{"id":u32(lib,p4),"range_count":u32(lib,p4+4),
                 "range_start":u32(lib,p4+8),"range_end":u32(lib,p4+12),
                 "sentinel_after_range":u32(lib,p4+16)},
        "thai_glyphs_mapped":len(thai),
        "thai_first":thai[:8],"thai_last":thai[-8:],
        "conclusion":"Pack 4 is explicitly the Thai U+0E00..U+0E7F pack. Do not swap it with U+3130..U+32FF; that is pack 3."
    }
    out=json.dumps(report,ensure_ascii=False,indent=2)
    if a.output:a.output.write_text(out+"\n",encoding="utf-8")
    print(out)
if __name__=="__main__": main()
