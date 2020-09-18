from flask import Flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from flask_cors import CORS
from back_end.API import socket, API
from back_end.auth import authenticator
app = Flask(__name__)

CORS(app, supports_credentials=True)

app.config['SECRET_KEY'] = 'super-secret-key'
app.config['JWT_SECRET_KEY'] = 'super-secret-key' # TODO: Can this just be SECRET_KEY?
application = DispatcherMiddleware(API, {
    '/auth': authenticator,
    '/socket': socket
})


if __name__ == '__main__':
    app.run(debug=True, use_debugger=False, use_reloader=False, passthrough_errors=True, port=4000  )
