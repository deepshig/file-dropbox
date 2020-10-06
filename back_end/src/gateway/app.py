from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room, ConnectionRefusedError
from flask_cors import CORS
import requests
import threading
import time
import json
import uuid
from datetime import datetime
import os
import shutil
import pathlib

app = Flask(__name__)
SECRET_KEY = "i5uitypjchnar0rlz31yh0u5sgs8rui2baxxgw8e"

app.config['SECRET_KEY'] = SECRET_KEY

INSIDE_CONTAINER = os.environ.get('IN_CONTAINER_FLAG', False)


CORS(app, supports_credentials=True)
socket = SocketIO(app, cors_allowed_origins="*")
file_path = os.path.abspath(pathlib.Path().absolute()) + '/'


def save_file(file):
    location = os.path.abspath(pathlib.Path().absolute())
    with open("file.gz", 'wb') as location:
        shutil.copyfileobj(file, location)
    del file


@socket.on('connect')
def connect():
    token = request.args.get('token')
    uid = request.args.get('uid')
    if INSIDE_CONTAINER:
        resp = requests.post("http://auth:4000/auth/testverify", data={'name': uid, 'token': token})
    else:
        resp = requests.post("http://127.0.0.1:4000/auth/testverify", data={'name': uid, 'token': token})

    print(resp.json()['verified'])

    if not resp.json()['verified']:
        raise ConnectionRefusedError('unauthorized!')
    else:

        print('someone connected to websocket')
        join_room(uid)
        emit('connect', {'data': 'connected'}, room=uid)
        emit('connected', {'data': 'connected'}, room=uid)


@socket.on('message')    # send(message=msg, broadcast=True)
def handleMessage(msg, headers):
    print(msg)
    emit('message', {'data': 'hello'})


@socket.on('alive')    # send(message=msg, broadcast=True)
def handleAlive(headers):
    emit('alive', {'alive': True}, room=headers['User'])


@socket.on('upload')    # send(message=msg, broadcast=True)
def handleAlive(msg, headers):
    print(msg['data'])
    save_file(msg['data'])
    emit('upload', {'upload': True})


@socket.on('start-transfer')
def start_transfer(filename, size):
    """Process an upload request from the client."""
    _, ext = os.path.splitext(filename)
    if ext in ['.exe', '.bin', '.js', '.sh', '.py', '.php']:
        return False  # reject the upload

    id = uuid.uuid4().hex  # server-side filename
    with open(file_path + id + '.json', 'wt') as f:
        json.dump({'filename': filename, 'size': size}, f)
    with open(file_path + id + ext, 'wb') as f:
        pass
    return id + ext  # allow the upload


@socket.on('write-chunk')
def write_chunk(filename, offset, data):
    """Write a chunk of data sent by the client."""
    # TODO: implement start transfer and file naming. Maybe paths aren't needed if forwarding to redis?
    _, ext = os.path.splitext(filename)
    if ext in ['.exe', '.bin', '.js', '.sh', '.py', '.php']:
        return False  # reject the upload

    id = uuid.uuid4().hex  # server-side filename
    with open(file_path + filename + '.json', 'wt') as f:
        json.dump({'filename': filename}, f)
    with open(file_path + filename, 'wb') as f:
        pass
    try:
        with open(file_path + filename, 'r+b') as f:
            f.seek(offset)
            f.write(data)
    except IOError:
        print(IOError)
        return False
    print("trying")
    return True


@socket.on('complete-upload')
def complete_upload(filename, username, user_id):
    print("Complete")
    with open(file_path + filename, 'rb') as f:
        if INSIDE_CONTAINER:
            resp = requests.post('http://api-uploader:3500/file/upload', files={'file': f, 'user_id': user_id, 'username': username})
        else:
            resp = requests.post('http://127.0.0.1:3500/file/upload', files={'file': f, 'user_id': user_id, 'username': username})
        print(resp.json())
        # os.remove(file_path + filename)
        emit('complete-upload', {'data': True})


class threads(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            socket.emit('test', {'data': 'test time: ' + datetime.now().strftime("%H:%M:%S")})
            time.sleep(5)


if __name__ == '__main__':
    thread = threads()
    thread.start()
    socket.run(app, debug=True, use_debugger=False, use_reloader=False,
               passthrough_errors=True, host="0.0.0.0", port=5000)
