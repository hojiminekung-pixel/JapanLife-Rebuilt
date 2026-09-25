from flask import Flask, request, jsonify
from datetime import datetime, timezone
import os

app = Flask(__name__)

@app.get('/health')
def health():
    return jsonify(ok=True, service='Japan Life compatibility server', time=datetime.now(timezone.utc).isoformat())

@app.route('/json/<path:endpoint>', methods=['GET', 'POST'])
def api(endpoint):
    payload = request.get_json(silent=True)
    if payload is None:
        payload = request.form.to_dict() or request.args.to_dict()

    if endpoint == 'util/version_check':
        return jsonify(result=0, success=True, version='1.5.12')
    if endpoint == 'get/get_setting':
        return jsonify(result=0, success=True, settings={})
    if endpoint == 'get/get_user':
        return jsonify(result=0, success=True, user={})
    if endpoint == 'get/get_game_data_url':
        return jsonify(result=0, success=True, url='')

    return jsonify(result=0, success=True, endpoint=endpoint, data={})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', '8080')))
