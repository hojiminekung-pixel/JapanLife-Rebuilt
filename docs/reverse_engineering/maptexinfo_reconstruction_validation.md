# Complete maptexinfo reconstruction validation

- Source: Japan Life 1.5.12 `res/raw/maptexinfo.smf`
- Source size: 662,615 bytes
- Header/hash area: 7,524 bytes
- Legacy descriptor records: 4,685
- Legacy descriptor bytes: 655,091
- Native descriptor bytes: 343,943
- Reconstructed file size: 351,467 bytes

## Record conversion

Every legacy record is parsed with:

`size = 7 + 4 * legacy_point_count`

The native 1.5.12 loader consumes only the first half of those coordinate bytes, so reconstruction emits:

`field_02 + field_03 + legacy_count + first_half_coordinates + original_payload_offset`

No IDs, flags, coordinates from the retained half, or payload offsets are invented.

## Cross-check

All 4,685 records were mapped to the texture chunk order in `mapdata000..mapdata234`.

- Payload-offset mismatches: **0**
- Native records parsed: **4,685 / 4,685**
- Native parser stop/error: **none**
- Trailing descriptor bytes: **0**
