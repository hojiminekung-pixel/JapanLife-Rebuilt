# Japan Life 1.5.12 — recovered server protocol notes

## Confirmed
- API base: https://japanlife.nubee.com/json/
- Version check: POST /json/util/version_check
- Request field: test_cmd = "vcheck"
- Response parser reads response[1]["major"] and response[1]["minor"] as strings.
- Compatibility response: [{}, {"major":"1","minor":"5"}]

## Patch bypass recovered from a known 1.5.12 offline-fix build
The archived OFFLINE-FIX native library changes exactly three functions:
- CPatchManager::HasUpdates -> immediate false
- CPatchManager::ValidateChecksum -> immediate false
- CPatchManager::CheckNeedUpdate -> immediate false
The three changes total 12 bytes.

## Current server strategy
The server logs every request and provides conservative acknowledgements for the recovered endpoint surface. Exact schemas are still being recovered from native response parsers; unknown endpoints return HTTP 501.

## Event-bundle / shop visual finding 2026-09-26
Native symbols and strings confirm a dedicated event-bundle endpoint:
- GET endpoint: get/get_bundle_events
- response fields: bundle_id, shop_id, start_datetime, end_datetime, bundle_items
- bundle item fields: item_type, value

The client therefore obtains the event-bundle list from the server, while the actual building/item artwork is resolved through the native resource/texture system. The event-bundle JSON itself does not contain the rendered texture.

The base 1.5.12 data_bundle.smf contains a Sakura theme bundle whose building values include:
- 2067
- 2080
- 2089

The native binary also contains the event/gacha texture enum TEX_GACHA_BUNDLE_MOMOTAIRO, but no corresponding Sakura Lucky Bag gacha-image enum was found in the verified base native string table. This is consistent with the screenshot showing the generic red placeholder for the Sakura event bundle: the bundle metadata exists, but the corresponding late-content visual resource is part of the missing patch/resource layer rather than the base APK.

Do not patch the renderer blindly. First recover the event/patch texture resource or build a verified compatibility replacement.

## Font finding 2026-09-25
The exact 1.5.12 native metadata confirms pack 3 is U+3130..U+32FF and pack 4 is U+0E00..U+0E7F (Thai). DetermineLanguage() already maps Thai into pack 4. The previous range-swap experiment was therefore incorrect and has been removed. The remaining font bug is downstream of pack selection, in font-cache/glyph-texture construction or lookup. The APK contains res/raw/font.smf and the native code contains BuildFontTexture, ReadFromCacheFile, RestoreCachedTextureTable, g_aushOffset and g_asTextureTable.

## Next server milestone
Recover exact response schemas for get_game_data_url and save/load endpoints from native response parsers. Do not return generic success objects for these endpoints because the client expects typed nested fields.

## Next asset milestone
Recover the missing late-content event-bundle texture layer (starting with Sakura/Lucky Bag) and map its artwork to the verified base building IDs/resources. Keep the known-good Thai/font baseline unchanged.
