from flask import Flask
# from back_end import app
from flask_socketio import SocketIO, send, emit
from flask_cors import CORS
import random
from time import sleep

# TODO Import flask error. Export flask=, pycharm
app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret-key'
CORS(app)

socketIO = SocketIO(app, cors_allowed_origins="*")


@socketIO.on('connect')
def test_connect():
    print('someone connected to websocket')
    emit('responseMessage', {'data': 'Connected! ayy'})


@socketIO.on('message')
def handleMessage(msg):  # TODO: Seperate Messages or JSON'ed?
    print(msg)
    # send(message=msg, broadcast=True)
    if msg["status"] == "On":
        for i in range(5):
            emit('responseMessage', {'temperature': round(random.random() * 10, 3)})
            sleep(.5)
    return None

@socketIO.on('upload')
def handleUpload(msg):  # TODO: Seperate Messages or JSON'ed?
    print(msg)
    # send(message=msg, broadcast=True)
    if msg["status"] == "On":
        for i in range(5):
            emit('responseMessage', {'temperature': round(random.random() * 10, 3)})
            sleep(.5)
    return None


if __name__ == '__main__':
    app.run(debug=True, use_debugger=False, use_reloader=False, passthrough_errors=True, port=5000)
