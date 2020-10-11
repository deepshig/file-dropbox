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
# import etcd

app = Flask(__name__)
SECRET_KEY = "i5uitypjchnar0rlz31yh0u5sgs8rui2baxxgw8e"

app.config['SECRET_KEY'] = SECRET_KEY

INSIDE_CONTAINER = os.environ.get('IN_CONTAINER_FLAG', False)


CORS(app, supports_credentials=True)
socket = SocketIO(app, cors_allowed_origins="*")
file_path = os.path.abspath(pathlib.Path().absolute()) + '/tmp/'


@socket.on('connect')
def connect():
    """
    Passing of args to host::/connect through headers or JSON query.

    headers={'user_id': user_id, 'access_token': access_token}

    or

    query: {access_token: store.getState().authentication.token, user_id: store.getState().authentication.user_id},

    :parameter access_token: retrieved from request.args.get('access_token') or token = request.headers['access_token']
    :parameter user_id: retrieved from request.args.get('user_id') or token = request.headers['user_id']
    :return:
    """
    if request.args.get('access_token') is not None:
        token = request.args.get('access_token')
        user_id = request.args.get('user_id')
    elif request.headers['access_token'] is not None:
        token = request.headers['access_token']
        user_id = request.headers['user_id']
    if INSIDE_CONTAINER:
        resp = requests.get("http://auth:4000/auth/validate", data={'user_id': user_id, 'access_token': str(token)})
    else:
        resp = requests.get("http://127.0.0.1:4000/auth/validate", data={'user_id': user_id, 'access_token': str(token)})

    print(resp.status_code)

    if not resp.status_code == 200:
        raise ConnectionRefusedError('unauthorized!')
    else:
        print('someone connected to websocket')
        join_room(user_id)
        emit('connect', {'data': 'connected'}, room=user_id)
        emit('connected', {'data': 'connected'}, room=user_id)


@socket.on('message')    # send(message=msg, broadcast=True)
def handleMessage(msg):
    """

    :param msg:
    :return:
    """
    # print(msg)
    emit('message', {'data': 'hello : ' + str(msg['client_id'])})


@socket.on('alive')    # send(message=msg, broadcast=True)
def handleAlive(headers):
    """

    :param headers:
    :return:
    """
    emit('alive', {'alive': True}, room=headers['user_id'])


@socket.on('start-transfer')
def start_transfer(filename, size):
    """
    Process an upload request from the client.

    :param filename:
    :param size:
    :return:
    """

    print("starting")
    _, ext = os.path.splitext(filename)
    if ext in ['.exe', '.bin', '.js', '.sh', '.py', '.php']:
        return False  # reject the upload

    id = uuid.uuid4().hex  # server-side filename
    with open(file_path + id + '.json', 'wt') as f:
        json.dump({'filename': filename, 'size': size}, f)
    with open(file_path + id, 'wb') as f:
        pass
    emit('start-transfer', {'id': id})
    return id  # TODO: return an emit? this line? ^^


@socket.on('write-chunk')
def write_chunk(filename, offset, data):
    """

    :param filename:
    :param offset:
    :param data:
    :return:
    """
    # TODO: implement start transfer and file naming. Maybe paths aren't needed if forwarding to redis?
    # _, ext = os.path.splitext(filename)
    # if ext in ['.exe', '.bin', '.js', '.sh', '.py', '.php']:
    #     return False  # reject the upload
    #
    # id = uuid.uuid4().hex  # server-side filename
    with open(file_path + filename, 'wb') as f:
        pass
    try:
        with open(file_path + filename, 'r+b') as f:
            f.seek(offset)
            f.write(data)
    except IOError:
        print(IOError)
        return False
    return True


@socket.on('complete-upload')
def complete_upload(file_id, username, user_id):
    """

    :param file_id:
    :param username:
    :param user_id:
    :return:
    """
    print(file_id)
    # file_id = file_id.split('tmp/')[1]
    print("Complete")
    print(user_id)
    with open(file_path + file_id + '.json', 'rb') as f:
        data = json.load(f)
        data = json.dumps(data)
        # data = pickle.dump()
        print(data)
    with open(file_path + file_id, 'rb') as f:
        if INSIDE_CONTAINER:
            resp = requests.post('http://file-uploader:3500/file/upload', files={'file': f, 'user_id': user_id, 'user_name': username, 'meta': data})
        else:
            resp = requests.post('http://127.0.0.1:3500/file/upload', files={'file': f, 'user_id': user_id, 'user_name': username, 'meta': data})
        # resp.status_code = 201
        print(resp.content)
        if resp.status_code == 201:
        # status_code = 201
        # print(status_code)
        # if status_code == 201:
            emit('complete-upload', {'data': True})
        else:
            print(resp)
            emit('complete-upload', {'data': False})


class threads(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            socket.emit('test', {'data': 'test time: ' + datetime.now().strftime("%H:%M:%S")})
            time.sleep(5)


if __name__ == '__main__':
    port = 5000
    # if INSIDE_CONTAINER:
    #     client = etcd.Client(host='etcd', port=2379)
    #
    # else:
    #     client = etcd.Client(host='127.0.0.1', port=2379)
    #
    # print(client.machines)
    # client.write('/nodes/n1', 5000)
    # print(client.read('/nodes/n1').value)
    thread = threads()
    thread.start()
    socket.run(app, debug=True, use_debugger=False, use_reloader=False,
               passthrough_errors=True, host="0.0.0.0", port=port)
