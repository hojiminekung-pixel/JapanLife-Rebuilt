# Japan Life compatibility server

This is a reconstruction target for the original Japan Life v1.5.12 client.
It is not a replacement game. The goal is to reproduce the HTTP/JSON contract expected by the original native client.

## Confirmed client endpoints

The original native library contains the base API URL https://japanlife.nubee.com/json/ and many endpoint paths under /json/.

Historical app documentation explicitly described Japan Life as an online game, and the service ended on 6 January 2016.

## Current implementation

The Flask app provides a health endpoint and deterministic baseline responses for the first four endpoints. Unknown endpoints return a development response so the protocol can be implemented incrementally.

## Next reverse-engineering step

Recover the native request builders and response parsers around CActualServer, CGameServer, and CQueryManager. Record exact parameter names, HTTP method, headers, and JSON fields before making the server authoritative.
