#!/usr/bin/env python3
"""Build the verified baseline APK without the previously speculative font-range swap.

Pack metadata recovered from the 1.5.12 native library:
  pack 3 = U+3130..U+32FF
  pack 4 = U+0E00..U+0E7F (Thai)

The native client already maps Thai to pack 4. This tool therefore only copies
the APK while removing the old experimental range-swap logic. Font rendering
must be debugged in cache/glyph construction, not by changing pack ownership.
"""
import argparse, zipfile
from pathlib import Path
LIB="lib/armeabi/libKyotoLife.so"
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("apk",type=Path); ap.add_argument("-o","--output",type=Path,required=True); a=ap.parse_args()
    with zipfile.ZipFile(a.apk) as zin, zipfile.ZipFile(a.output,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=9) as zout:
        for info in zin.infolist():
            if info.filename.upper().startswith("META-INF/"): continue
            zout.writestr(info,zin.read(info.filename))
    print("mode: thai-pack4-baseline (no speculative range swap)")
if __name__=="__main__": main()
