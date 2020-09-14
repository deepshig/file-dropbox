from flask import Flask
app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/views')
def views():
    return 'Hello, World!'  # Talk to File service manager to call user table
