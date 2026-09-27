# World Life 0.1 — Map/Structure Recovery Plan

Audit date: 2026-09-28

## Master findings

The current Master-derived APK contains 235 mapdata resources (mapdata000.smf through mapdata234.smf).

Confirmed transparent 2x2 placeholder payloads: 122/235.

IDs:
0, 59, 78, 88, 92, 100, 105-113, 123, 129-234.

These are not simply missing ZIP entries. The resource files exist but their payloads are transparent placeholders.

## Do not replace blindly

The renderer can reference map texture IDs through maptexinfo.smf and packed resources. A replacement image inserted at the wrong ID can produce incorrect terrain/buildings or crash the native renderer.

Safe sequence:
1. Decode/validate maptexinfo.smf.
2. Build a mapdata -> texture/container reference table.
3. Cross-reference data_building.smf and building identifiers.
4. Cross-reference NPC/player/animation resources.
5. Recover a matching original visual where the reference mapping proves it belongs there.
6. If a visual cannot be recovered, create a new original replacement with the same logical footprint/category.
7. Validate dimensions, alpha, compression/container format and resource ID.
8. Test one mapdata group at a time.
9. Keep the original Master untouched.

## Building catalog

data_building.smf is present and contains the historical building catalog, including House, Factory, Attraction, Deco, Utility, Path and landmark identifiers. This is the canonical source for logical building identity while visuals are reconstructed.

## External references

Public documentation confirms Japan Life was a Japanese-themed city/tourism builder with 100+ buildings/items and Japanese architecture. These sources are useful as visual/gameplay references, not as permission to copy third-party copyrighted assets:
- https://www.metacritic.com/game/japan-life/details/
- https://www.4gamer.net/games/160/G016013/
- https://android-app.roof-balcony.com/game/simulation/japanlife/
- https://japanlife.fandom.com/wiki/Japan_Life_Wiki

## Acceptance criteria

- No placeholder mapdata remains in an area that is actually referenced by the active map.
- Existing map geometry and gameplay IDs remain unchanged.
- New replacements have deterministic IDs and backups.
- The game reaches the map, settings and relaunch tests without a crash.
