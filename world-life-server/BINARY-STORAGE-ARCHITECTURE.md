# World Life Binary Storage Architecture

Status: ready for binary-resource rollout.

- GitHub stores source code, manifests, and documentation.
- Supabase Storage bucket: world-life-resources
- Resource path: resources/<filename>
- legacy-resource Edge Function serves the binary and emits x-resource-sha256.
- Resource manifest remains the authoritative mapping between native enum, Master filename, size, and SHA-256.
- The working Master APK is not modified by this infrastructure change.
- patch.bin remains disabled until an original-compatible patch payload is independently validated.

First rollout target:
- mapdata000.smf
- Master size: 28686 bytes
- Master SHA-256: 90ca3be14e53991b09ad0a802dd70636021ccac7a0e5bee70522b14c51c1edc2

Binary uploads must be performed through an actual binary/object-storage upload path. Do not base64-encode a binary into GitHub text files.
