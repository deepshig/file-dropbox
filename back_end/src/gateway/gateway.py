from __future__ import print_function
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
import pika
import pathlib
import sys
from config import config
from rabbitmq import RabbitMQManager
# import etcd

import logging
import logging.handlers


app = Flask(__name__)

SECRET_KEY = "i5uitypjchnar0rlz31yh0u5sgs8rui2baxxgw8e"
app.config['SECRET_KEY'] = SECRET_KEY

INSIDE_CONTAINER = os.environ.get('IN_CONTAINER_FLAG', False)


CORS(app, supports_credentials=True)
socket = SocketIO(app, cors_allowed_origins="*")
file_path = os.path.abspath(pathlib.Path().absolute()) + '/tmp/'

print(config["rabbitmq_config"])


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def send_message(event, msg):
    """

    :param event:
    :param msg:
    :return:
    """
    print(msg)
    emit(event, {'data': msg})


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
    Handles a message event and responds with hello

    :param msg: receive any JSON format message from a client. Needs 'client_id' in data
    :return: {'data': 'hello : ' + str(msg['client_id'])}
    """
    # print(msg)
    emit('message', {'data': 'hello : ' + str(msg['client_id'])})


@socket.on('alive')    # send(message=msg, broadcast=True)
def handleAlive(headers):
    """
    When queried replies to user that they are successfully hitting the service.

    :param headers: headers['user_id']
    :return: {'alive': True}, room=headers['user_id']
    """
    emit('alive', {'alive': True}, room=headers['user_id'])


@socket.on('start-transfer')
def start_transfer(filename, size):
    """
    Prepare for an upload request from the client. Generates a UUID for the requested file,
    client then uses this file_id for uploading a unique file.

    :param filename: Desired npy file.
    :param size: byte size of file being uploaded
    :return: emit('start-transfer', {'id': id})
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
    Writes chunks at an offset for the file identified by the given UUID

    :param filename: UUID returned from start_transfer
    :param offset: chunk sizes
    :param data: data packet
    :return:
    """

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
    Complete the upload process by reading completed file, matching with metadata uploaded at
    start_transfer. Send these two files to the uploader service.

    :param file_id: UUID from start_transfer
    :param username: text username
    :param user_id: user_id passed from auth service
    :return: emit('complete-upload', {'data': Boolean})
    """
    print(file_id)
    # file_id = file_id.split('tmp/')[1]
    print("Complete")
    print(user_id)
    with open(file_path + file_id + '.json', 'rb') as f:
        data = json.load(f)
        data = json.dumps(data)
        # data = pickle.dump()
        eprint(data)
        eprint(type(data))
    with open(file_path + file_id, 'rb') as f:
        eprint("sending")
        if INSIDE_CONTAINER:
            resp = requests.post('http://file-uploader:3500/file/upload', files={'file': f}, data={'user_id': user_id, 'user_name': username, 'metadata': data})
        else:
            resp = requests.post('http://127.0.0.1:3500/file/upload', files={'file': f}, data={'user_id': user_id, 'user_name': username, 'metadata': data})
        # resp.status_code = 201
        eprint(resp.content)
        if resp.status_code == 201:
        # status_code = 201
        # print(status_code)
        # if status_code == 201:
            emit('complete-upload', {'data': True})
        else:
            eprint(resp)
            emit('complete-upload', {'data': False})

@socket.on('get-history')
def getHistory(data, headers):
    print(data['user_id'])
    if INSIDE_CONTAINER:
        resp = requests.get('http://fsm:4500/client/history/' + data['user_id'])
    else:
        resp = requests.get('http://127.0.0.1:4500/client/history/' + data['user_id'])

    emit('get-history', {'data': resp.content.decode("utf-8")})
    print(resp.content)


class threads(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            socket.emit('test', {'data': 'test time: ' + datetime.now().strftime("%H:%M:%S")})
            time.sleep(5)


class RBMQThread(threading.Thread):
    def __init__(self, ):
        threading.Thread.__init__(self)
        self.queue_manager = RabbitMQManager(config['rabbitmq_config'])
        self.queue_manager.chan.basic_qos(prefetch_count=1)

    def run(self):
        # define the queue consumption
        self.queue_manager.chan.basic_consume(queue=self.queue_manager.queue_name,
                                         on_message_callback=self.callback)
        # start consuming
        self.queue_manager.chan.start_consuming()

    def callback(self, ch, method, props, body):
        resp = self.queue_manager.receive_msg(ch, method, props, body)
        print(resp)
        my_json = resp.decode('utf8').replace("'", '"')
        data = json.loads(my_json)
        s = json.dumps(data, indent=4, sort_keys=True)
        d = json.loads(s)
        print(d)
        print(type(d))
        logging.info(d)
        socket.emit('admin', {'data': d}) # TODO: recieve then process, then ack
        # send_message('admin', resp)


if __name__ == '__main__':
    port = 5000
    logger = logging.getLogger()
    fh = logging.handlers.RotatingFileHandler(filename=config["logging"]["file_path"], maxBytes=10240, backupCount=5)
    # fh.setLevel(logging.DEBUG)#no matter what level I set here
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.setLevel(logging.INFO)
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
    rbmq = RBMQThread()
    rbmq.start()
    socket.run(app, debug=True, use_debugger=False, use_reloader=False,
               passthrough_errors=True, host="0.0.0.0", port=port)
