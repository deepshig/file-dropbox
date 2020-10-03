from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room, ConnectionRefusedError
from flask_cors import CORS
import requests
import threading
import time

app = Flask(__name__)
SECRET_KEY = "i5uitypjchnar0rlz31yh0u5sgs8rui2baxxgw8e"

app.config['SECRET_KEY'] = SECRET_KEY
app.config['SECRET_KEY'] = 'secret!'

CORS(app, supports_credentials=True)
socket = SocketIO(app, cors_allowed_origins="*")


@socket.on('connect')
def test_connect():
    token = request.args.get('token')
    uid = request.args.get('uid')
    resp = requests.post("http://localhost:4000/auth/testverify", data={'name': uid, 'token': token})
    print(resp.json()['verified'])

    if not resp.json()['verified']:
        raise ConnectionRefusedError('unauthorized!')
    else:

        print('someone connected to websocket')
        join_room(uid)
        emit('connected', {'data': 'connected'}, room=uid)
        # emit('connected', {'data': 'connected'}, room=uid)


@socket.on('message')    # send(message=msg, broadcast=True)
def handleMessage(msg, headers):
    print(msg)
    emit('message', {'data': 'hello'})


@socket.on('alive')    # send(message=msg, broadcast=True)
def handleAlive(headers):
    emit('alive', {'alive': True}, room=headers['User'])


class threads(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            socket.emit('test', {'data': 'test'})
            time.sleep(5)


if __name__ == '__main__':
    thread = threads()
    thread.start()
    socket.run(app, debug=True, use_debugger=False, use_reloader=False,
            passthrough_errors=True, host="0.0.0.0", port=50000)
