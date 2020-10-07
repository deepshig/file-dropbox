import os
import json
import requests
import threading
import time
import random
import jwt
import socketio

global user_name
global user_id
global access_token
global host


class Client(threading.Thread):
    def __init__(self, id, socket):
        threading.Thread.__init__(self)
        self.id = id
        self.socket = socket
        self.file = ''

        @socket.event
        def message(data):
            print(str(self.id) + ': Received data: ', data)

    def run(self):
        self.socket.connect("http://" + host + ":5000/", headers={'user_id': user_id, 'access_token': access_token})
        print(str(self.id) + ": Connected")
        while True:
            self.socket.emit("message", {'user_id': user_id, 'access_token': access_token, 'client_id': self.id})
            time.sleep(random.randint(1, 3))


if __name__ == "__main__":
    numClients = 10
    host = '127.0.0.1'
    user_name = "hello"
    resp = requests.put("http://" + host + ":4000/auth/login/" + user_name)
    resp = resp.json()
    decoded = jwt.decode(resp['jwt'], verify=False)
    user_id = decoded['user_id']
    access_token = decoded['access_token']
    # print(jwt.decode(resp['jwt'], verify=False))

    # print(jwt.decode(resp['jwt']))
    thread = []
    for i in range(numClients):
        thread.append(Client(i, socketio.Client()))

    for t in thread:
        t.start()
