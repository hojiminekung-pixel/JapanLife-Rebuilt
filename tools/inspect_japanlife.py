#!/usr/bin/env python3
import argparse, hashlib, json, re, zipfile
from pathlib import Path

THAI = re.compile(rb'[\xe0\xb8\x80-\xe0\xb9\xbf]')

def sha256(data):
    return hashlib.sha256(data).hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("apk", type=Path)
    args = ap.parse_args()

    with zipfile.ZipFile(args.apk) as z:
        names = z.namelist()
        native = [n for n in names if n.endswith(".so")]
        smf = [n for n in names if n.endswith(".smf")]
        result = {
            "apk": str(args.apk),
            "size": args.apk.stat().st_size,
            "entries": len(names),
            "native_libraries": {},
            "smf": {},
        }

        for n in native:
            b = z.read(n)
            result["native_libraries"][n] = {
                "size": len(b),
                "sha256": sha256(b),
            }

        for n in smf:
            b = z.read(n)
            result["smf"][n] = {
                "size": len(b),
                "sha256": sha256(b),
                "thai_utf8_triplets": len(THAI.findall(b)),
            }

    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
