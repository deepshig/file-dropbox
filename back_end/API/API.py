from flask import Flask, request, redirect, url_for, session, json, make_response, jsonify
from flask_cors import CORS, cross_origin
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity

import uuid
app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config['JWT_SECRET_KEY'] = 'super-secret-key'
jwt = JWTManager(app)

# TODO: Unite apps to single Flask instance, or well define ports, or route from main API.

@app.route('/api/')
def index():
    return 'Hello, World!'


@app.route('/api/views')
def views():
    return 'Hello, World!'  # Talk to File service manager to call user table


if __name__ == '__main__':
    app.run(debug=True, use_debugger=False, use_reloader=False, passthrough_errors=True)
