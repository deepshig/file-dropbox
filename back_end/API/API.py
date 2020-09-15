from flask import Flask, request, redirect, url_for, session, json, make_response
from flask_cors import CORS, cross_origin
import json
import uuid
app = Flask(__name__)

# CORS(app, support_credentials=True, origins=["http://127.0.0.1:5000"])
# CORS(app, resources={r"/*": {"origins": "*"}})
CORS(app, supports_credentials=True)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route('/api/')
def index():
    return 'Hello, World!'


@app.route('/api/views')
def views():
    return 'Hello, World!'  # Talk to File service manager to call user table


@app.route('/auth/test', methods=['POST'])
def test():
    if request.method == 'POST':
        t = request.get_json()
        session['username'] = t['UID']
        response = make_response("Session Cookie")
        # response = redirect(url_for('index'))
        key = str(uuid.uuid4())
        # response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.set_cookie('session_id', key)
        # print(key)
        return response
    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True, use_debugger=False, use_reloader=False, passthrough_errors=True)
