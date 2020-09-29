from flask import Flask, Blueprint, request
from flask_cors import CORS, cross_origin
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_socketio import SocketIO, send, emit
import random
from time import sleep

from back_end.src.auth.authenticator import auth_blueprint
from back_end.API import socket_blueprint

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret-key'

jwt = JWTManager(app)

CORS(app, supports_credentials=True)
socket = SocketIO(app, cors_allowed_origins="*")

app.register_blueprint(auth_blueprint)
app.register_blueprint(socket_blueprint)


@socket.on('connect')
def test_connect():
    print(get_jwt_identity())
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
                emit('responseMessage', {'temperature': round(random.random() * 10, 3)})
                sleep(.5)
    return None


if __name__ == '__main__':
    app.run(debug=True, use_debugger=False, use_reloader=False,
            passthrough_errors=True, port=4000)
    # socket.run(app, port=4000)
