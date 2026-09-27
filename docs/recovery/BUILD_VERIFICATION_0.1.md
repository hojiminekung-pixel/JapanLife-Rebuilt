# World Life 0.1 — build verification record

Generated from the current stability-test APK outside Git history.

## Artifacts

- Stability test APK SHA-256: bfecb5f6b5a3dead92b180ab5f1309d3b157f49f77c38150db8490a32967e5d8
- Branded test APK SHA-256: 8ef3b053546004bc61345b5a6a82cac1971a66a0c4cbb4be4b72f8003246d9dd
- App label string: World Life (patched in the branded test build)
- Package namespace: com.nubee.japanlife (kept unchanged for compatibility)
- Native library: lib/armeabi/libKyotoLife.so
- Version target: 0.1

## Verified resource observations

- mapdata000.smf through mapdata234.smf are present.
- The mapdata set contains transparent 2x2 placeholder payloads; these must be mapped through maptexinfo/packed resources before replacement.
- data_building.smf, data_npc.smf, data_player.smf, data_animation.smf, start_town.smf and maptexinfo.smf are present.
- The original social-login Java/native integration is still present in the current APK. It is intentionally not deleted yet because the email-auth replacement must be proven first.

## Current test build scope

The branded test APK only changes the visible app label from Japan Life to World Life on top of the stability-test APK. It does NOT claim to have completed email authentication, map recovery, Dukku player binding, staff NPC binding, or BGM replacement.

## Required device regression

1. Install branded test APK (uninstall an APK signed by a different certificate first).
2. Launch.
3. Create character.
4. Enter map.
5. Open Settings.
6. Return to map.
7. Force-close.
8. Relaunch.
9. Repeat Settings test.
10. Record any crash screen/log before making another native change.

## Master rule

The master APK remains immutable. No experimental APK is to overwrite or replace it.
