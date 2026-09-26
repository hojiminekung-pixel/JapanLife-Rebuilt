#!/usr/bin/env python3
"""Collect native ARM font-runtime evidence from an original Japan Life APK.

Diagnostic only: this does not modify libKyotoLife.so. The Thai pack is already
proven to be pack 4; the remaining question is where Thai glyphs are lost
between cache restoration, glyph-table lookup, and texture construction.
"""
from __future__ import annotations
import argparse, hashlib, json, re, struct, zipfile
from pathlib import Path

LIB = "lib/armeabi/libKyotoLife.so"
FONT = "res/raw/font.smf"
NEEDLES = [
    b"BuildFontTexture", b"ReadFromCacheFile", b"RestoreCachedTextureTable",
    b"g_aushOffset", b"g_asTextureTable", b"DrawCharacter",
    b"font.smf", b"cache", b"texture",
]
P4 = struct.pack("<IIIII", 4, 2, 0x0E00, 0x0E7F, 0xFFFFFFFF)

def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def elf_info(b: bytes) -> dict:
    out={"magic":b[:4].hex(),"class":None,"machine":None,"endian":None}
    if b[:4] != b"\x7fELF": return out
    out["class"]={1:"ELF32",2:"ELF64"}.get(b[4],str(b[4]))
    if b[5] == 1:
        out["endian"]="little"; out["machine"]=struct.unpack_from("<H",b,18)[0]
    elif b[5] == 2:
        out["endian"]="big"; out["machine"]=struct.unpack_from(">H",b,18)[0]
    return out

def printable_runs(b: bytes, minlen: int=5):
    return [(m.start(),m.group().decode("latin1","replace"))
            for m in re.finditer(rb"[ -~]{%d,}" % minlen,b)]

def find_all(b: bytes, needle: bytes):
    out=[]; start=0
    while True:
        i=b.find(needle,start)
        if i<0: return out
        out.append(i); start=i+1

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("apk",type=Path)
    ap.add_argument("-o","--output",type=Path)
    a=ap.parse_args()
    with zipfile.ZipFile(a.apk) as z:
        lib=z.read(LIB); font=z.read(FONT)
    runs=printable_runs(lib)
    hits={n.decode():[hex(x) for x in find_all(lib,n)] for n in NEEDLES}
    p4hits=[hex(x) for x in find_all(lib,P4)]
    thai_utf8=[]
    for m in re.finditer(rb"[\xe0-\xe9][\x80-\xbf][\x80-\xbf]",font):
        thai_utf8.append({"offset":hex(m.start()),"hex":m.group().hex()})
    report={
      "apk":str(a.apk),
      "native":{"path":LIB,"size":len(lib),"sha256":sha256(lib),"elf":elf_info(lib)},
      "font":{"path":FONT,"size":len(font),"sha256":sha256(font)},
      "native_string_hits":hits,
      "pack4_descriptor_raw_hits":p4hits,
      "nearby_printable_strings":[
        {"offset":hex(o),"text":s} for o,s in runs
        if any(k.decode("latin1").lower() in s.lower() for k in NEEDLES)
      ][:200],
      "thai_utf8_sequences_in_font":thai_utf8[:200],
      "next_step":"Recover xrefs from these native data/string locations and trace cache restoration -> glyph table -> texture construction. This tool intentionally makes no native patch."
    }
    out=json.dumps(report,ensure_ascii=False,indent=2)+"\n"
    if a.output: a.output.write_text(out,encoding="utf-8")
    print(out,end="")
if __name__=="__main__": main()
