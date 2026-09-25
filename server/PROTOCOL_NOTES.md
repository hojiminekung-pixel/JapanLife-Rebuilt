# Japan Life 1.5.12 — recovered server protocol notes

These notes record only behavior recovered from the original lib/armeabi/libKyotoLife.so in the supplied Japan Life 1.5.12 APK.

## Version check

Native call chain:

CGameServer::TryCheckVersion() → CGameServer::SendPacket() → CActualServer::PostData().

The original API base is:
https://japanlife.nubee.com/json/

The version-check endpoint is:
util/version_check

The request object is constructed with:
- test_cmd = vcheck

The native response parser indexes the returned JSON as an array and reads:
- response[1]["major"] as a string
- response[1]["minor"] as a string

The compatibility server therefore returns:

    [
      {},
      {"major":"1","minor":"5"}
    ]

This replaces the earlier guessed {result, success, version} response, which was not supported by the native parser.

## Patch/server behavior

CActualServer::PostData() parses the HTTP body with JsonCpp and exposes the parsed JSON to the caller. HTTP success alone is therefore insufficient; the response JSON shape must match the native caller's parser.

## Next targets

Recover the exact schemas for get/get_setting, get/get_user, patch-data requests, save/load, currency, friends/network, and event endpoints before implementing them. Unknown endpoints intentionally return HTTP 501 so protocol gaps are visible during testing rather than silently producing misleading data.
