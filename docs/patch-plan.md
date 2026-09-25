# Patch plan

## 1. Preserve the original game

The target is the existing Japan Life APK, not a recreation.

The first rule for every patch is:

1. copy the original APK;
2. verify the expected native library and resource hashes;
3. modify only the intended bytes/files;
4. rebuild and sign;
5. compare the resulting APK contents against the original;
6. keep a machine-readable patch manifest.

## 2. Thai square-glyph problem

The APK contains:

- `lib/armeabi/libKyotoLife.so`
- `res/raw/font.smf`
- native symbols/strings associated with `CFontRenderer`
- Thai-specific renderer helpers such as vowel/tone/ascender handling.

The previous experimental change changed one byte in the native library, but it did not fix the visible Thai squares. Therefore that change is **not** treated as the final solution.

Next investigation:

1. identify the code path from `DetermineLanguage()` to font-pack selection;
2. identify the table used by `RestoreSpecialFontTextureTable()` / font texture restoration;
3. map Thai code points to the corresponding glyph records in `font.smf`;
4. verify whether the glyph exists but its atlas/UV/texture ID is wrong;
5. patch the smallest table or code path that fixes Thai;
6. test Thai base characters, upper/lower vowels, tone marks, sara-am and combining marks.

## 3. Crash / compatibility

Do not replace the game engine.

Instead:

- inspect the Android manifest and native ABI requirements;
- inspect startup JNI/native loading;
- compare crashes by device/API level;
- patch only the failing compatibility path;
- keep `armeabi/libKyotoLife.so` and all original game data unless evidence requires a change.

## 4. Build strategy

Prefer direct APK surgery for this closed binary:

- preserve all original entries;
- replace only patched native/resource entries;
- remove stale signature metadata;
- zipalign;
- sign the resulting APK.

If direct surgery becomes insufficient, use Apktool as a controlled fallback for manifest/resources/smali work.
