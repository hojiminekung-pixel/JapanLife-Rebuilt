import hashlib
import sys

ORIGINAL_SHA256 = "0d82ff380548030163eb46be396d672ddb41832f8307680d2a1b14faaf9b3b1f"
PATCHED_SHA256 = "c2fcf24f3399832622f3c7325c3fa5090c15e5abaed487c23c919d87cb418af5"
OFFSET = 0x133CB4
OLD = bytes.fromhex("10b525f1")
NEW = bytes.fromhex("00207047")

path = sys.argv[1]
data = bytearray(open(path, "rb").read())
before = hashlib.sha256(data).hexdigest()
if before != ORIGINAL_SHA256:
    raise SystemExit(f"Refusing to patch unexpected libKyotoLife.so: {before}")

if data[OFFSET:OFFSET+4] != OLD:
    raise SystemExit("Refusing to patch: original 4-byte sequence is not present")

data[OFFSET:OFFSET+4] = NEW
after = hashlib.sha256(data).hexdigest()
if after != PATCHED_SHA256:
    raise SystemExit(f"Patch produced unexpected SHA-256: {after}")

open(path, "wb").write(data)
print(f"Verified native patch applied: {before} -> {after}")
