# Native layout notes — SObjDisplay / maptexinfo

## Verified constants

- mapdata count from maptexinfo header: **235**
- maptexinfo hash table: **235 SHA-256 values**
- native object-display stride: **0x2c = 44 bytes**
- native object-display end offset: **0x3253c bytes**
- 0x3253c / 0x2c = **4685 object-display slots**
- packed-texture/mapdata split constant in `CObjTexManager::GetTexture`: **0x124c = 4684**
- map-backed EMAPTEX IDs therefore begin after the packed-texture range checked by the native branch.

## SObjDisplay fields directly observed in native code

| Offset | Native use |
|---:|---|
| 0x00 | 16-bit EMAPTEX identifier; used as the key by `GetObjDisplay(EMAPTEX)` |
| 0x02 | 8-bit value copied from maptexinfo; also participates in display-derived size/count calculations |
| 0x03 | 8-bit value copied from maptexinfo |
| 0x08 | pointer to an array of 2D float coordinates |
| 0x0c | 32-bit mapdata-relative payload offset used by `GetTexture` |
| 0x10 | derived float value; native code initializes it from the two byte fields |
| 0x14 | initialized to zero |
| 0x24 | coordinate count after native normalization |
| 0x26 | texture-cache slot/index; initialized to -1 |
| 0x28 | initialized to null |

The coordinate array is populated from signed 16-bit X/Y values and converted to floats.

## Texture source selection

`GetTexture(SObjDisplay&)` first checks the EMAPTEX ID against 0x124c.

For IDs above that threshold, the native code:

1. divides the EMAPTEX ID by 20,
2. selects the corresponding decompressed mapdata buffer,
3. adds `SObjDisplay+0x0c` to that buffer,
4. reads the payload type,
5. dispatches to PNG/PVR/raw texture loading as appropriate.

This is the key mapping path that will be used for the reconstruction rather than guessing from byte-pattern matches.

## What remains unresolved

The exact **serialized descriptor format** feeding the 4685 `SObjDisplay` slots still needs to be reconstructed. The native initialization loop is variable-length and includes a coordinate list plus additional fields, so the repeated `01 01 18` pattern is not a safe record delimiter.

The next implementation step is therefore a native-faithful stream parser that reproduces the pointer movement in `CObjectDataManager::Initialize()` and validates the resulting 4685 entries against the runtime field invariants.

No texture replacement should be generated until that parser passes those invariants.
