# maptexinfo.smf — native reconstruction checkpoint

Date: 2026-09-26

## Baseline

Verified Japan Life 1.5.12 APK:

- `res/raw/maptexinfo.smf`: 662,615 bytes
- first uint32: 235
- 235 * 32-byte SHA-256 table
- descriptor source starts at offset 7,524
- 235 hashes match the decompressed `mapdata000..mapdata234` payloads

## Native format recovered

ARMv7 Thumb tracing of `CObjectDataManager::Initialize()` gives the runtime descriptor format:

- 2 bytes: `field_02`, `field_03`
- 1 signed byte: coordinate-count encoding
- native stores that byte as u16 and logically shifts right by 1
- then reads `count/2` pairs of signed 16-bit `(x,y)`
- then reads a 32-bit mapdata-relative payload offset

The runtime table contains exactly **4,685 SObjDisplay slots** (stride 0x2c / 44 bytes).

## Breakthrough: the APK contains the complete source descriptor stream

The packaged descriptor region is **not missing**. It is a legacy/expanded serialization of the same 4,685 descriptors.

Using the legacy boundary rule:

`legacy_record_size = 7 + 4 * legacy_point_count`

the complete stream parses exactly:

- 3,338 records from offset 7,524 to 459,626
- 1,347 records from 459,626 to 662,615
- total: **4,685 records**
- no trailing bytes

The repeated `01 01 18` sequence is therefore a scan signature inside this stream, not a fixed 103-byte semantic record.

### Conversion rule

Each legacy record stores twice as many coordinate bytes as the 1.5.12 native loader consumes.

For each record:

1. preserve the two flag bytes;
2. preserve the legacy count byte;
3. keep only the **first half** of the legacy coordinate bytes;
4. move the original final 32-bit payload offset immediately after those coordinates.

This produces:

`native_record_size = 7 + 2 * legacy_point_count`

No speculative values are introduced.

The conversion reduces the descriptor region from 655,091 bytes to 343,943 bytes and produces a 351,467-byte complete native maptexinfo file including the 7,524-byte header/hash area.

## Independent validation

All **4,685** converted payload offsets match the sequential texture chunks found in `mapdata000..mapdata234`:

- mapdata index = `EMAPTEX // 20`
- slot within mapdata = `EMAPTEX % 20`
- PNG chunks and NBC-compressed texture chunks are both recognized
- 4,685 / 4,685 payload offsets match exactly

The reconstructed file was then fed through the native-format parser:

- 4,685 / 4,685 records parsed
- no invalid count
- no trailing bytes
- 4,685 / 4,685 payload offsets remain valid

## What this fixes

This reconstructs the missing **maptexinfo runtime serialization** without changing:

- EMAPTEX IDs
- mapdata files
- SHA-256 validation hashes
- texture payload bytes
- native rendering code
- resource names

The next stage is therefore asset/runtime testing, not another speculative reverse-engineering rewrite.

## Files

The reproducible converter is:

`tools/reconstruct_maptexinfo_native.py`

It takes the original packaged `maptexinfo.smf`, converts the legacy descriptor representation to the exact native 1.5.12 representation, and can validate all 4,685 payload offsets against mapdata000..234.
