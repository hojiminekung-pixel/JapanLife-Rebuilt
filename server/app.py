from flask import Flask, request, jsonify
from datetime import datetime, timezone
import logging, os

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Protocol recovered from the original Japan Life 1.5.12 native client.
# API base: https://japanlife.nubee.com/json/
# Version check: POST /json/util/version_check
# Request key: test_cmd = "vcheck"
# Response parser: response[1]["major"], response[1]["minor"]

KNOWN_VERSION = [
    {},
    {"major": "1", "minor": "5"},
]


def _payload():
    payload = request.get_json(silent=True)
    if payload is None:
        payload = request.form.to_dict() or request.args.to_dict()
    return payload


@app.get("/health")
def health():
    return jsonify(
        ok=True,
        service="Japan Life compatibility server",
        protocol="1.5.x",
        time=datetime.now(timezone.utc).isoformat(),
    )


@app.route("/json/<path:endpoint>", methods=["GET", "POST"])
def api(endpoint):
    payload = _payload()
    logging.info("API %s %s payload=%s", request.method, endpoint, payload)

    if endpoint == "util/version_check":
        return jsonify(KNOWN_VERSION)

    # Do not fabricate protocol responses for endpoints whose native response
    # schema has not yet been recovered. A visible 501 is safer for testing.
    return jsonify({
        "error": "endpoint_schema_not_recovered",
        "endpoint": endpoint,
        "method": request.method,
    }), 501


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
