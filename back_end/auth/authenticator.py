from flask import Flask, request, redirect, url_for, session, json, make_response, jsonify
from flask_cors import CORS, cross_origin
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity

import uuid
app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config['JWT_SECRET_KEY'] = 'super-secret-key'
jwt = JWTManager(app)


@app.route('/auth/test', methods=['POST'])
def test():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON request"}), 400
    UID = request.json.get('UID', None)
    if not UID:
        return jsonify({"msg": "Missing UID parameter"}), 400
    if UID != 'test':
        return jsonify({"msg": "Bad UID request"}), 400
    access_token = create_access_token(identity=UID)
    return jsonify(access_token=access_token), 200


@app.route('/auth/protected', methods=['GET'])
@jwt_required
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


if __name__ == '__main__':
    app.run(debug=True, use_debugger=False, use_reloader=False, passthrough_errors=True)
