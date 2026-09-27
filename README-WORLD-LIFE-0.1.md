# World Life 0.1 — Master build pipeline

This branch is a build pipeline for the original Master APK payload.

Important:
- The source of truth is the original Master `สร้างเกมสำเร็จ.zip`.
- This branch does NOT replace the game with the old Godot prototype.
- `main` is intentionally left unchanged.
- The workflow rebuilds the Master, sets Android app label to **World Life**, version to **0.1**, and verifies the resulting APK before uploading it as a GitHub Actions artifact.
- The character PNGs are staged under `world-life-assets/`; actual native character-slot mapping remains a separate repair step.

Input file required:
`master-input/world-life-master.zip`

After the input is present, run:
Actions → World Life Master APK 0.1 → Run workflow.

The workflow must fail rather than silently building the wrong source.
