from flask import Flask, request, jsonify
from datetime import datetime, timezone
import logging, os, uuid
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
KNOWN_VERSION = [{}, {"major": "1", "minor": "5"}]
def _payload():
    payload = request.get_json(silent=True)
    if payload is None: payload = request.form.to_dict() or request.args.to_dict()
    return payload or {}
def _generic_object():
    return {"result":1,"success":1,"status":1,"error":0,"error_code":0,"message":"","data":{},"results":[]}
@app.get("/health")
def health():
    return jsonify(ok=True, service="Japan Life compatibility server", protocol="1.5.x", time=datetime.now(timezone.utc).isoformat())
@app.route("/json/<path:endpoint>", methods=["GET","POST"])
def api(endpoint):
    payload=_payload(); logging.info("API %s %s payload=%s",request.method,endpoint,payload)
    if endpoint=="util/version_check": return jsonify(KNOWN_VERSION)
    if endpoint in {"get/get_setting","get/get_user","get/get_user_id","get/get_user_currency_balance","get/get_friends","get/get_friend_available_action","get/get_credibility","get/get_game_data_url","get/get_refund_cash","util/get_feature_item","util/get_sale_item","get/get_black_diamond_shop_items","get/get_gacha_unlocked_templates","get/get_train_msg","get/get_rotating_featured_items","get/get_active_gacha_event","get/get_cross_promotions_list","get/get_referral_event","get/get_helper_friends"}: return jsonify(_generic_object())
    if endpoint.startswith("save/") or endpoint.startswith("clear/") or endpoint.startswith("move/"):
        out=_generic_object(); out["request_id"]=str(uuid.uuid4()); return jsonify(out)
    return jsonify({"error":"endpoint_schema_not_recovered","endpoint":endpoint,"method":request.method}),501
if __name__=="__main__": app.run(host="0.0.0.0",port=int(os.environ.get("PORT","8080")))
