#!/usr/bin/env python3
from __future__ import annotations
import argparse, zipfile
from pathlib import Path
LIB="lib/armeabi/libKyotoLife.so"
PATCHES={0x238d20:(bytes.fromhex("70b570"),bytes.fromhex("00207047")),0x239390:(bytes.fromhex("f0b55f46"),bytes.fromhex("00207047")),0x239710:(bytes.fromhex("f0b55f46"),bytes.fromhex("00207047"))}
def patch(data):
    out=bytearray(data)
    for off,(old,new) in PATCHES.items():
        if data[off:off+len(old)]!=old: raise SystemExit(f"precondition failed at 0x{off:x}: got {data[off:off+len(old)].hex()}")
        out[off:off+len(new)]=new
    return bytes(out)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("apk",type=Path); ap.add_argument("-o","--output",type=Path,required=True); a=ap.parse_args()
    with zipfile.ZipFile(a.apk) as zin:
        patched=patch(zin.read(LIB)); a.output.parent.mkdir(parents=True,exist_ok=True)
        with zipfile.ZipFile(a.output,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=9) as zout:
            for info in zin.infolist():
                if info.filename.upper().startswith("META-INF/"): continue
                zout.writestr(info,patched if info.filename==LIB else zin.read(info.filename))
    print("patched exact offline functions: HasUpdates, ValidateChecksum, CheckNeedUpdate")
if __name__=="__main__": main()
