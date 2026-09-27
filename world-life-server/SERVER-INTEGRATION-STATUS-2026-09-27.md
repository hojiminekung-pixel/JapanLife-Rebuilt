# World Life Server Integration Status — 2026-09-27

## Master source
The game client source of truth is the original Master archive `สร้างเกมสำเร็จ.zip`, not the rebuilt GitHub client.

## Server
- Supabase project: `hgsugqaswxxkrsalvkci`
- Game: World Life
- Version: 0.1
- Legacy API contract: legacy-v1
- Public compatibility gateway: `/functions/v1/w`
- Resource gateway: `/functions/v1/legacy-resource`
- Patch setting remains disabled.

## Client test build
A server-routing test APK was generated from the known-good Master-based World Life APK. Only the native server URL pointers in `lib/armeabi/libKyotoLife.so` were redirected for the boot-critical legacy endpoints; the remaining APK files are unchanged.

Redirected endpoints:
- get_user
- get_user_id
- set_password
- save_user
- save_version
- get_game_data_url
- version_check
- get_setting
- original patch/CDN base

Server-test APK SHA-256:
`d1596b871706668587406ae19884208e5eb7c7d66680f691a32184cb7d8b076b`

## Patch test
The reconstructed patch.bin is 115 bytes and is built from the exact Master `mapdata000.smf` resource:
- resource size: 28686 bytes
- resource SHA-256: `90ca3be14e53991b09ad0a802dd70636021ccac7a0e5bee70522b14c51c1edc2`
- patch SHA-256: `41a10474ffcb3be6f073d3169cc66e3adfd91a50ed12a1cf2c944cb510bb28fd`

The patch is served by the compatibility gateway for structural testing, but production patching remains disabled until the actual resource delivery path is verified.

## Remaining binary delivery
The Supabase Storage bucket `world-life-resources` exists, but the actual binary resources have not yet been uploaded. Current `legacy_resource_objects` row count is 0.

Therefore this status intentionally does not claim that full binary resource delivery is complete.
