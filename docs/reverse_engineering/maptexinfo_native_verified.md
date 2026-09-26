# maptexinfo.smf — native-verified reverse-engineering checkpoint

Date: 2026-09-26

## Baseline

The verified Japan Life 1.5.12 APK contains `res/raw/maptexinfo.smf` with:

- file size: 662,615 bytes
- first uint32 (little-endian): 235
- next 235 * 32 bytes: SHA-256 table
- geometry/descriptor stream starts at offset 7,524
- the 235 SHA-256 entries match the decompressed mapdata000..mapdata234 payloads

## Native-code findings

Static analysis of `libKyotoLife.so` is now being used as the authoritative format reference.

### CObjTexManager::LoadMapData(int)

The native loader:

1. reads a mapdata resource,
2. decompresses it,
3. calculates SHA-256,
4. compares it against `CObjectDataManager::GetObjDisplayHashChecksum(mapIndex)`,
5. stores the decompressed mapdata buffer for texture lookup.

This confirms the first 235 hashes in maptexinfo are the mapdata validation table.

### CObjectDataManager::GetObjDisplay(EMAPTEX)

The native lookup uses a table of `SObjDisplay` entries with a stride of 0x2c (44 bytes). The lookup key is an `EMAPTEX` value.

This means the maptexinfo stream is not itself a simple 103-byte-per-entry table.

### CObjTexManager::GetTexture(SObjDisplay&)

The native texture loader confirms:

- `SObjDisplay + 0x00`: EMAPTEX identifier.
- `SObjDisplay + 0x08`: pointer to an array of 2D coordinates used during texture/object rendering.
- `SObjDisplay + 0x0c`: offset into the selected decompressed mapdata payload for map-backed textures.
- `SObjDisplay + 0x24`: coordinate-count field used to iterate the coordinate array.
- `SObjDisplay + 0x26`: texture-cache slot/index.
- For EMAPTEX values above the packed-texture threshold, the native code selects a mapdata index using integer division by 20 and then reads the texture payload at the per-display offset.

The packed-texture path and mapdata-backed path are therefore distinct.

## Important correction to the previous checkpoint

The earlier workspace report described the repeated `01 01 18` byte pattern as a fixed 103-byte record family.

Native-code tracing shows that this is **not safe to treat as the semantic record boundary**. The byte pattern occurs inside the variable-length descriptor stream. It should be retained only as a scan signature until the complete native parser is reconstructed.

The 103-byte occurrences remain useful for correlation, but they must not be used to rewrite texture mappings by themselves.

## Next reconstruction layer

1. Reconstruct the complete variable-length maptexinfo descriptor parser from `CObjectDataManager::Initialize()`.
2. Recover the actual object-display count and descriptor boundaries from the native initialization path.
3. Decode every EMAPTEX entry into:
   - EMAPTEX id
   - coordinate count
   - coordinate list
   - mapdata index/texture source
   - payload offset
   - cache index
4. Cross-check each mapping against the corresponding mapdata payload and packed texture archive.
5. Only after the mapping is native-verified, reconstruct missing placeholder texture/object assets.
6. Keep all original systems, IDs, resource names, and rendering paths intact unless a replacement is explicitly required.

## Safety rule for reconstruction

Do not replace `libKyotoLife.so` or rewrite maptexinfo mappings by guesswork. The next build should be generated from native-verified mappings and then tested against the original resource hashes and runtime loading path.
