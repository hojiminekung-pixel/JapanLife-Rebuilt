# World Life patch.bin format — native-verified v3

Verified directly against libKyotoLife.so Thumb disassembly.

Header: minimum 0x40 bytes.
- 0x00..0x07: ASCII magic ` FPN0001`
- 0x08..0x0B: uint32 LE version `0x00240001`
- 0x0C..0x0D: uint16 LE flags/reserved, must be 0
- 0x14..0x17: uint32 LE record count
- 0x20..0x3F: stored SHA-256

Native validation copies the complete candidate, zeroes bytes 0x18..0x3F, hashes the entire candidate, and compares that hash with the stored digest at 0x20.

Records start at 0x40 and are variable length:
- +0x00: 32-byte SHA-256
- +0x20: uint32 LE resource size
- +0x24: NUL-terminated resource filename

ReadPatchFile resolves each filename through CAppResourceManager::GetEnumFromFilename().

Verified empty structural artifact:
- size 64 bytes
- SHA-256 1f7550c08af844f4abb53b5c672519178c14812ef397c79af2930e34cfc644c1
- header digest cd20fed1c1033dd45935fd3f62256e32109ccbc62692109560f25f2640abe452

Production patching remains disabled until a real resource patch is hosted and tested end-to-end.
