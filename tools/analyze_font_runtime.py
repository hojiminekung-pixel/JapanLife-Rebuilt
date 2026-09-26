#!/usr/bin/env python3
"""Collect native ARM font-runtime evidence from an original Japan Life APK.

This is deliberately diagnostic: it does not modify libKyotoLife.so. The Thai
pack is already proven to be pack 4, so the next question is where a Thai
codepoint is lost between cache restoration, glyph-table lookup and texture
construction.

The report records:
- native library SHA-256 and ELF architecture;
- presence/offsets of font-runtime strings;
- nearby printable strings that help identify the owning native routines;
- raw occurrences of the known pack-4 descriptor bytes;
- a deterministic list of Thai UTF-8 strings embedded in the APK.

If GNU objdump is available, the workflow can optionally attach a disassembly
snippet around the relevant native string addresses.
"""
from __future__ import annotations
import argparse, hashlib, json, re, struct, subprocess, zipfile
from pathlib import Path

LIB = "lib/armeabi/libKyotoLife.so"
FONT = "res/raw/font.smf"
NEEDLES = [
    b"BuildFontTexture", b"ReadFromCacheFile", b"RestoreCachedTextureTable",
    b"g_aushOffset", b"g_asTextureTable", b"DrawCharacter",
    b"font.smf", b"cache", b"texture",
]
P4 = struct.pack("<IIIII", 4, 2, 0x0E00, 0x0E7F, 0xFFFFFFFF)

def sha256(b): return hashlib.sha256(b).hexdigest()

def elf_info(b):
    out={"magic":b[:4].hex(),"class":None,"machine":None}
    if b[:4] != b"\x7fELF": return out
    out["class"] = {1:"ELF32",2:"ELF64"}.get(b[4],str(b[4]))
    if b[5] == 1:
        out["endian"]="little"
        out["machine"]=struct.unpack_from("<H",b,18)[0]
    elif b[5] == 2:
        out["endian"]="big"
        out["machine"]=struct.unpack_from(">H",b,18)[0]
    return out

def printable_runs(b, minlen=5):
    return [(m.start(),m.group().decode("latin1","replace"))
            for m in re.finditer(rb"[ -~]{%d,}" % minlen,b)]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("apk",type=Path)
    ap.add_argument("-o","--output",type=Path)
    a=ap.parse_args()
    with zipfile.ZipFile(a.apk) as z:
        lib=z.read(LIB); font=z.read(FONT)
    runs=printable_runs(lib)
    hits={}
    for n in NEEDLES:
        pos=[]; start=0
        while True:
            i=lib.find(n,start)
            if i<0: break
            pos.append(hex(i)); start=i+1
        hits[n.decode()]=pos
    p4hits=[]; start=0
    while True:
        i=lib.find(P4,start)
        if i<0: break
        p4hits.append(hex(i)); start=i+1
    thai_strings=[]
    for m in re.finditer(rb"[\xe0-\xe9][\x80-\xbf][\x80-\xbf]+",font):
        thai_strings.append({"offset":hex(m.start()),"hex":m.group().hex()})
    report={
      "apk":str(a.apk),
      "native":{"path":LIB,"size":len(lib),"sha256":sha256(lib),"elf":elf_info(lib)},
      "font":{"path":FONT,"size":len(font),"sha256":sha256(font)},
      "native_string_hits":hits,
      "pack4_descriptor_raw_hits":p4hits,
      "nearby_printable_strings":[{"offset":hex(o),"text":s} for o,s in runs if any(k.decode() in s.lower() for k in [x.lower() for x in NEEDLES])][:200],
      "thai_utf8_sequences_in_font":thai_strings[:200],
      "next_step":"Use the native string/xref locations to recover the cache read -> glyph table -> texture path. No font-pack ownership is changed by this tool."
    }
    out=json.dumps(report,ensure_ascii=False,indent=2)+"\n"
    if a.output:a.output.write_text(out,encoding="utf-8")
    print(out,end="")
if __name__=="__main__": main()
