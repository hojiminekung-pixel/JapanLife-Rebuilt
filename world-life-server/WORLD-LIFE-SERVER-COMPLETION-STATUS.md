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

## Patch format — native-confirmed v2
Direct Thumb disassembly of `CPatchData::ValidatePatchFileData()` and `CPatchData::ReadPatchFile()` now confirms:

- file length must be at least `0x40` bytes
- bytes `0x00..0x07` are ASCII ` FPN0001`
- uint32 LE at `0x08` must equal `0x00240001`
- uint16 LE at `0x0c` must equal `0`
- uint32 LE at `0x14` is the patch-record count
- SHA-256 is stored at `0x20..0x3f`
- for checksum calculation the native code copies the whole candidate, clears `0x18..0x3f`, hashes the complete candidate, and compares the result with `0x20..0x3f`
- first on-disk record begins at `0x40`
- each on-disk record is:
  - 32-byte resource SHA-256
  - uint32 LE resource size
  - NUL-terminated resource filename
- the native loader converts the filename to the game's `EFILE` resource enum using `GetEnumFromFilename()`

A one-resource manifest for the real Master resource `mapdata000.smf` / logical filename `mapdata000.nbc` was generated and passed an independent reimplementation of these native checks.

This is a structural validation artifact only. It is not enabled as production patch data.

## Native patch delivery evidence
`CPatchManager::Initialise()` reads an external patch file before calling `CPatchData::ReadPatchFile()`.

`CPatchManager::ValidateChecksum()` iterates the parsed patch records and calls `CPatchData::CheckHash()` against both packaged/external hash locations as appropriate.

`CPatchManager::CheckNeedUpdate()` compares resource hashes and, when the required external file exists, can use the native external-file copy/delete path to reconcile the patched resource.

Therefore `patch.bin` is confirmed as a manifest/index; replacement resource bytes are delivered separately. A fake manifest without matching external resources is not useful and will not be enabled.

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
`get_game_data_url` still returns an empty download URL/size/checksum. Patch delivery remains disabled until binary hosting and the complete resource-delivery contract are verified.

## Next production gate
1. Finish the exact patch/download path and external resource location contract.
2. Host the patch manifest and matching binary resources on stable HTTPS.
3. Retarget the native HTTP layer without modifying gameplay/resource logic.
4. Build a separate server-test APK.
5. Test boot/version/settings/login/save/update paths before touching the working APK.
