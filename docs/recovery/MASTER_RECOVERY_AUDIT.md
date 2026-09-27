# World Life — Master Recovery Audit (2026-09-28)

This repository is the build/tooling repository. The 51 MB native APK master is kept outside Git history because the current GitHub workflow is not the correct place for a large binary master.

## Locked source

- Master APK: `World-Life-0.1-branded.apk`
- The Master remains read-only.
- Every experimental APK must be derived from a copy and must carry a unique test label.

## Findings from the actual Master APK

### Resource inventory

- 235 `mapdata000.smf` … `mapdata234.smf` files are present.
- 122 of those resources contain a transparent 2×2 PNG payload.
- 105 IDs from `mapdata129` through `mapdata233` are byte-for-byte identical placeholder payloads.
- `mapdata234` is another transparent 2×2 placeholder with a different compressed wrapper.
- 16 earlier IDs also contain transparent 2×2 placeholders: 0, 59, 78, 88, 92, 100, 105–113, 123.
- `data_building.smf` and its large decompressed catalog are still present.
- `data_npc.smf`, `data_player.smf`, `data_animation.smf`, `start_town.smf`, and `maptexinfo.smf` are present.

### Native crash candidate

The Master native library differs from the original v1.5.12 library by exactly four bytes. The changed bytes are the beginning of the exported `CSaveDataManager::IsExternalStorageAvailable()` function.

The Master currently makes that function return immediately with zero, while the original contains the original function body. A separate stability-test APK restores only these four bytes. This test must be evaluated before changing any other native behavior.

## Required implementation order

1. Stabilize launch → character creation → map → Settings → relaunch.
2. Preserve the working Thai font path and the current World Life branding.
3. Map placeholder mapdata IDs to `maptexinfo`, packed textures and the native resource manager before replacement.
4. Recover original assets where they still exist.
5. For unrecoverable assets, create clearly marked new replacements rather than silently treating them as originals.
6. Keep the original social-login implementation/resources backed up while the new email flow is implemented.
7. Implement Email/Gmail-style authentication against World-Life-Server.
8. Implement approval state on the server before granting account access.
9. Replace the visible legacy Nubee branding with Dukku only at verified UI/resource callsites; do not rename native package/JNI symbols blindly.
10. Bind the crowned black Dukku duck as the starter/player character.
11. Bind the crownless black Dukku duck as staff/tutorial NPCs.
12. Add the multi-outfit fallback library for tutorial/dialogue characters.
13. Replace BGM with a new original relaxing nature track while retaining the original audio as backup.
14. Validate patch delivery only after the native client patch format and checksum behavior are understood.
15. Build a final APK only after all regression tests pass.

## Safety rules for every build

- Never overwrite the Master.
- Never replace a native function with an unconditional return merely to hide a crash.
- Never delete the old login assets until the replacement is proven end-to-end.
- Every APK gets a unique filename, SHA-256, and test purpose.
- Test one subsystem change at a time when debugging crashes.
