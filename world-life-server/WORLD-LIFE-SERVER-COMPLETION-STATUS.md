# World Life — Legacy Server Completion Status

Updated 2026-09-27.

## Master preservation
The authoritative client is the uploaded Master archive `สร้างเกมสำเร็จ.zip`. The existing branded World Life 0.1 APK is kept as the working baseline. The Master is not overwritten.

## Native resource map
- 437 native resource enums were mapped deterministically.
- enum 0 = `maptexinfo.dat`
- enums 1–235 = `mapdata000.nbc` … `mapdata234.nbc`
- enum 236 = `packed0.png`
- enums 237–322 = `packed1.nbc` … `Packed86.nbc`
- enums 323–436 = data/message/font/effect/airport/UI resources.
- The Master resource package contains the mapped resources and was verified at approximately 44.8 MB.

## Font evidence
`font.smf` and `eswfont.smf` in the Master are byte-identical to the supplied Japan Life v1.5.12 APK resources. They must not be replaced speculatively. The square-glyph problem is therefore not evidence that the embedded font bytes are missing.

## Patch format evidence
The native patch validator requires:
- magic: ASCII ` FPN0001`
- header marker at offset 0x08: `0x00240001`
- reserved field at 0x0c is required to be zero
- file count is read at offset 0x14
- SHA-256 material is checked around offset 0x20
- first patch record begins at offset 0x40
- patch records contain a filename and resource enum mapping; the exact checksum coverage and record semantics still require an original patch sample before a production patch.bin is generated.

No fake patch.bin is being enabled.

## Legacy API
The live Supabase Edge Function is:
`legacy-api-full` (ACTIVE v1, public endpoint with JWT verification disabled by design for this legacy client contract).

Implemented core endpoints:
- `/json/util/version_check`
- `/json/get/get_setting`
- `/json/get/get_user_id`
- `/json/get/get_user`
- `/json/move/set_password`
- `/json/get/get_game_data_url`
- `/json/save/save_user`
- `/json/save/save_user_frequent`
- `/json/save/save_version`
- `/json/save/save_udid_migration`
- `/json/rollback/get_game_data`

The native client contract confirms useful response data is read from JSON index 1 for the core calls, so responses are wrapped as `[0,payload]`.

## Current server safety state
`get_game_data_url` still returns an empty download URL/size/checksum. Patch delivery remains disabled until binary hosting and the exact patch checksum contract are verified.

## Next production gate
1. Obtain or reconstruct a verified original `patch.bin` contract.
2. Host the patch/data payload on a stable HTTPS endpoint.
3. Retarget the native HTTP layer without modifying gameplay/resource logic.
4. Build a separate server-test APK.
5. Test boot/version/settings/login/save/update paths before touching the working APK.
