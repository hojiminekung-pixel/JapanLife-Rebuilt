# World-Life-Server

This repository is **server / tooling / Master-data support only**.

## Master baseline

The original **Master APK** is the sole game baseline. Game systems, maps, SMF resources, native library, NPCs, characters, buildings, vehicles, animations, textures, and other gameplay changes must be applied to the Master data path—not to a Godot recreation.

The repository must not be treated as a replacement game project.

## Server layer

The repository contains the World-Life-Server support layer, including Cloudflare gateway, Supabase configuration, patch/resource tooling, and controlled resource manifests.

No unverified native binary patch is published.

## Validation rule

Any Master modification must preserve the original resource format and pass integrity/package validation before it can be considered a release candidate.
