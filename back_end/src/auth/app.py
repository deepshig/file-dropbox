from flask import Flask, make_response, jsonify
from flask_restful import Resource, Api, output_json
from . import authentication_service, user_db
# import authentication_service
# import user_db

app = Flask(__name__)
api = Api(app)

ERROR_ROLE_NOT_FOUND = "Invalid role"
ERROR_INTERNAL_SERVER = "Internal Server Error"

db_config = {"user": "postgres",
             "password": "postgres",
             "host": "127.0.0.1",
             "port": "5432",
             "db_name": "user_auth"}

accepted_roles = ["admin", "user", "developer"]


def init(db_config):
    db = user_db.UserDB(db_config)
    svc = authentication_service.Authenticator(db)
    return svc


class Ping(Resource):
    def get(self):
        return output_json({"ping": "pong"}, 200)


api.add_resource(Ping, '/ping')

if __name__ == '__main__':
    app.run(debug=True, use_debugger=False, use_reloader=False,
            passthrough_errors=True, port=3000)
