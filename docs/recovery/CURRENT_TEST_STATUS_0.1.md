# World Life 0.1 — Current Test Build Status

## Builds

- Branded/stability line: World-Life-0.1-branded-test.apk
- Nature BGM candidate: World-Life-0.1-nature-bgm-test.apk

The nature-BGM candidate changes only `res/raw/sound_bgm.ogg` from the branded/stability test line. It is a separate test artifact and does not overwrite the Master.

## Music

A new original 76.93-second relaxing nature-style BGM was generated in OGG/Vorbis, 44.1 kHz stereo. It is intentionally gentle and loop-friendly. Device testing is required before treating it as the final game BGM.

## Character targets

- Player: black duck with crown.
- Staff: black duck without crown.
- Tutorial/guide characters: multiple non-repeating outfits.

Character resource binding is still a native-resource task and must be mapped before replacement to avoid crashes.

## Map targets

122 of 235 mapdata resources are confirmed transparent 2x2 placeholders. They must be mapped through `maptexinfo.smf` and packed resources before replacement.

## Authentication

World-Life-Server database/approval workflow has been hardened. Old social-login resources remain backed up until email signup/verification/approval/login passes end-to-end.
