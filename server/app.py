from flask import Flask, request, jsonify
from datetime import datetime, timezone
import logging, os

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Recovered from the original v1.5.12 native client (libKyotoLife.so):
# CGameServer::TryCheckVersion -> CActualServer::PostData
# POST https://japanlife.nubee.com/json/util/version_check
# Request JSON contains: {"test_cmd": "vcheck"}
# The response is parsed as a JSON array; element 1 is read for string
# fields "major" and "minor".  Do not replace this with an invented
# {result, success, version} object: the native parser does not use that shape.

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.get("/health")
def health():
    return jsonify(
        ok=True,
        service="Japan Life compatibility server",
        time=datetime.now(timezone.utc).isoformat(),
    )


def _payload():
    payload = request.get_json(silent=True)
    if payload is None:
        payload = request.form.to_dict() or request.args.to_dict()
    return payload


@app.route("/json/<path:endpoint>", methods=["GET", "POST"])
def api(endpoint):
    payload = _payload()
    logging.info("API %s %s payload=%s", request.method, endpoint, payload)

    if endpoint == "util/version_check":
        # Verified response shape used by TryVersionCheck().  The client
        # indexes response[1]["major"] and response[1]["minor"] as strings.
        return jsonify([
            {},
            {"major": "1", "minor": "5"},
        ])

    # Other endpoints remain deliberately diagnostic until their request and
    # response schemas are recovered from the native client.  Returning a
    # generic success object here would make protocol debugging misleading.
    return jsonify(
        error="endpoint_schema_not_recovered",
        endpoint=endpoint,
        method=request.method,
    ), 501


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
