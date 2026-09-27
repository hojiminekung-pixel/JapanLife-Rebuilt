# World Life 0.1 — exact v1.5.12 Master pipeline

This branch now uses the newly supplied **exact original Japan Life v1.5.12 APK** as the binary baseline.

Verified baseline:
- SHA-256: `710fe5887768ddb6f68c5bb192dd48335afe141491c13d16dce19d74fd2b2d71`
- APK size: 51,006,886 bytes
- Package: `com.nubee.japanlife`
- Version: `1.5.12`

The original APK and the previous Master were compared byte-for-byte:
- 637 common files are identical.
- `lib/armeabi/libKyotoLife.so` differs by exactly four bytes.
- The verified change is at offset `0x133CB4`, inside `CSaveDataManager::IsExternalStorageAvailable()`.
- `10 b5 25 f1` is replaced by `00 20 70 47`.
- This produces the known Master native SHA-256:
  `c2fcf24f3399832622f3c7325c3fa5090c15e5abaed487c23c919d87cb418af5`.

The workflow now:
1. Verifies the exact original APK hash.
2. Decodes the original APK directly with Apktool.
3. Applies only the verified four-byte native patch.
4. Changes Android label to **World Life** and version to **0.1**.
5. Rebuilds, aligns, signs and verifies the APK.
6. Uploads the resulting APK as a GitHub Actions artifact.

The character replacement is deliberately NOT injected as arbitrary PNG assets in this pipeline. Player/staff slot mapping will be done after the Master boots reliably, using the native resource/texture mapping already recovered.
