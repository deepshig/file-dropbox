from flask import Flask, Blueprint
from flask_socketio import SocketIO, send, emit
import random
from time import sleep
from . import socket_blueprint
from back_end.app import app

socket = SocketIO(app, cors_allowed_origins="*")


@socket_blueprint.route('/<something>',)
def test(something):
    print('hi %s', something)


@socket.on('connect')
def test_connect():
    print('someone connected to websocket')
    emit('responseMessage', {'data': 'Connected! ayy'})


@socket.on('message')
def handleMessage(msg):
    print(msg)
    # send(message=msg, broadcast=True)
    if msg["status"] == "On":
        for i in range(5):
            print("HIT")
            emit('responseMessage', {'temperature': round(random.random() * 10, 3)})
            sleep(.5)
    return None


# if __name__ == '__main__':
#     app.run(debug=True, use_debugger=False, use_reloader=False, passthrough_errors=True, port=5000)
