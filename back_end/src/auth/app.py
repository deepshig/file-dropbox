from flask import Flask, make_response, jsonify
from . import authentication_service
# import authentication_service

app = Flask(__name__)
svc = None

ERROR_ROLE_NOT_FOUND = "Invalid role"
ERROR_INTERNAL_SERVER = "Internal Server Error"

db_config = {"user": "postgres",
             "password": "postgres",
             "host": "127.0.0.1",
             "port": "5432",
             "db_name": "user_auth"}

accepted_roles = ["admin", "user", "developer"]

# TODO : proper dependency injection


def init(db_config):
    svc = authentication_service.Authenticator(db_config)
    return svc


@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"ping": "ping"}), 200


if __name__ == '__main__':
    svc = init(db_config)
    app.run(debug=True, use_debugger=False, use_reloader=False,
            passthrough_errors=True, port=3000)
