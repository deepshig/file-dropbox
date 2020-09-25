from flask import Blueprint

socket_blueprint = Blueprint('socket', __name__, url_prefix='/socket.io')

from . import socket