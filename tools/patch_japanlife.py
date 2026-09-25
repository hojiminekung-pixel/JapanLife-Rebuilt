#!/usr/bin/env python3
"""
Conservative Japan Life 1.5.12 font-pack experiment.

Verified native metadata shows FONTPACK_ID 4 has TWO Unicode ranges:
  primary  : U+3130..U+32FF
  secondary: U+0E00..U+0E7F (Thai)
DetermineLanguage() already maps Thai to pack 4.

The previous patch incorrectly changed only the primary range and therefore did
not address the two-range ordering hypothesis. This version swaps the two
ranges
without changing the language classifier. It is intentionally isolated so the
result can be A/B tested against the exact baseline.
"""
import argparse, hashlib, zipfile
from pathlib import Path
LIB="lib/armeabi/libKyotoLife.so"
PATCHES=[
 (0x2EFCF0, bytes.fromhex("30310000"), bytes.fromhex("000E0000")),
 (0x2EFCF4, bytes.fromhex("FF320000"), bytes.fromhex("7F0E0000")),
 (0x2EFF04, bytes.fromhex("000E0000"), bytes.fromhex("30310000")),
 (0x2EFF08, bytes.fromhex("7F0E0000"), bytes.fromhex("FF320000")),
]
def sha256(b): return hashlib.sha256(b).hexdigest()
def main():
 ap=argparse.ArgumentParser(); ap.add_argument("apk",type=Path); ap.add_argument("-o","--output",type=Path,required=True); a=ap.parse_args()
 with zipfile.ZipFile(a.apk) as z: original=z.read(LIB)
 out=bytearray(original)
 for off,old,new in PATCHES:
  got=original[off:off+4]
  if got!=old: raise SystemExit(f"precondition failed at 0x{off:x}: {got.hex()} != {old.hex()}")
  out[off:off+4]=new
 a.output.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(a.output,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=9) as zout:
  with zipfile.ZipFile(a.apk) as zin:
   for info in zin.infolist():
    if info.filename.upper().startswith("META-INF/"): continue
    zout.writestr(info,bytes(out) if info.filename==LIB else zin.read(info.filename))
 print("mode: thai-pack4-range-swap")
 print("original_sha256:",sha256(original))
 print("patched_sha256 :",sha256(out))
 print("thai_range     : U+0E00..U+0E7F")
 print("jamo_range     : U+3130..U+32FF")
if __name__=="__main__": main()
