from flask import Flask
# from back_end import app
from flask_socketio import SocketIO, send
from flask_cors import CORS
#
app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret-key'
CORS(app)

socketIO = SocketIO(app)

@socketIO.on('message')
def handleMessage(msg):
    print(msg)
    send(message=msg, broadcast=True)
    return None

if __name__ == '__main__':
    app.run(debug=True, use_debugger=False, use_reloader=False, passthrough_errors=True, port=4000  )
