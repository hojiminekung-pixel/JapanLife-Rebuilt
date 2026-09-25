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
