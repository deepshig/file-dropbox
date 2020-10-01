import jwt
from flask import Flask, make_response, jsonify, request
from flask_restful import Resource, Api, output_json, reqparse
from uuid import UUID
from src.auth import authentication_service
from src.auth import user_db
from flask_cors import CORS

from flask_jwt_extended import JWTManager, get_jwt_identity, decode_token
from flask_socketio import SocketIO, send, emit
import random
from time import sleep

app = Flask(__name__)
CORS(app, supports_credentials=True)
socket = SocketIO(app, cors_allowed_origins="*")

api = Api(app)

ERROR_ROLE_NOT_PROVIDED = "Role not provided"
ERROR_NAME_NOT_PROVIDED = "Name not provided"
ERROR_ROLE_NOT_FOUND = "Invalid role"
ERROR_INVALID_USER_ID = "Inavlid User ID"
ERROR_INVALID_USER_NAME = "Inavlid User Name"
ERROR_INTERNAL_SERVER = "Internal Server Error"

SECRET_KEY = "i5uitypjchnar0rlz31yh0u5sgs8rui2baxxgw8e"

app.config['SECRET_KEY'] = SECRET_KEY
jwtMng = JWTManager(app)

db_config = {"user": "postgres",
             "password": "postgres",
             "host": "127.0.0.1",
             "port": "5432",
             "db_name": "user_auth"}

accepted_roles = ["admin", "user", "developer"]


#####################################
#           Sockets                 #
#####################################

@socket.on('connect')
def test_connect():

    print('someone connected to websocket')
    if get_jwt_identity() is not None:
        emit('responseMessage', {'data': get_jwt_identity()})
    else:
        emit('responseMessage', {'data': 'Connected! ayy'})


@socket.on('message')    # send(message=msg, broadcast=True)
def handleMessage(msg, headers):
    print(msg)
    token = headers['extraHeaders']['Authorization'].split(" ")[1]
    print(token)
    if msg["status"] == "On":
        for i in range(5):
            if get_jwt_identity() is not None:
                emit('responseMessage', {'data': get_jwt_identity()})
            else:
                emit('responseMessage', {
                     'temperature': round(random.random() * 10, 3)})
                sleep(.5)
    return None


####################################
#       End Sockets                #
####################################


def init(db_config):
    db = user_db.UserDB(db_config)
    svc = authentication_service.Authenticator(db)
    return svc


def is_valid_uuid(uuid_str):
    try:
        uuid_obj = UUID(uuid_str, version=4)
    except ValueError:
        return False

    return str(uuid_obj) == uuid_str


def is_valid_user_name(user_name):
    cleaned_user_name = user_name.strip()
    return not (cleaned_user_name == "")


def create_jwt(payload):
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


class Ping(Resource):
    def get(self):
        return output_json({"ping": "pong"}, 200)


class CreateUser(Resource):
    def __init__(self, svc):
        self.svc = svc

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', required=True, type=str,
                            help=ERROR_NAME_NOT_PROVIDED)
        parser.add_argument('role', required=True, type=str,
                            help=ERROR_ROLE_NOT_PROVIDED)
        args = parser.parse_args()

        role, name = args["role"], args["name"]

        if role not in accepted_roles:
            return output_json({"msg": ERROR_ROLE_NOT_FOUND}, 400)

        user_details = svc.create_user(role, name)
        if user_details["user_created"]:
            user_details["id"] = str(user_details["id"])
            user_details["access_token"] = str(user_details["access_token"])
            jwt = create_jwt(user_details)
            return output_json({"jwt": jwt.decode()}, 201)
        else:
            return output_json({"msg": ERROR_INTERNAL_SERVER}, 500)


class LoginUser(Resource):
    def __init__(self, svc):
        self.svc = svc

    def put(self, user_name):
        if not is_valid_user_name(user_name):
            return output_json({"msg": ERROR_INVALID_USER_NAME}, 400)

        response = svc.login(user_name)
        if response["user_logged_in"]:
            response["access_token"] = str(response["access_token"])
            jwt = create_jwt(response)
            return output_json({"jwt": jwt.decode()}, 201)
        elif response["error"] == user_db.ERROR_USER_NOT_FOUND:
            return output_json(response, 400)
        else:
            return output_json({"msg": ERROR_INTERNAL_SERVER}, 500)


class LogoutUser(Resource):
    def __init__(self, svc):
        self.svc = svc

    def put(self, user_name):
        if not is_valid_user_name(user_name):
            return output_json({"msg": ERROR_INVALID_USER_NAME}, 400)

        response = svc.logout(user_name)
        if response["user_logged_out"]:
            return output_json(response, 200)
        elif response["error"] == user_db.ERROR_USER_NOT_FOUND:
            return output_json(response, 400)
        else:
            return output_json({"msg": ERROR_INTERNAL_SERVER}, 500)


svc = init(db_config)

api.add_resource(Ping, '/ping')
api.add_resource(CreateUser, '/auth/signup',
                 resource_class_kwargs={"svc": svc})
api.add_resource(LoginUser, '/auth/login/<string:user_name>',
                 resource_class_kwargs={"svc": svc})
api.add_resource(LogoutUser, '/auth/logout/<string:user_name>',
                 resource_class_kwargs={"svc": svc})

if __name__ == '__main__':
    app.run(debug=True, use_debugger=False, use_reloader=False,
            passthrough_errors=True, host='0.0.0.0', port=3000)
