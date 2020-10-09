import os
import json
import uuid

import requests
import threading
import time
import random
import jwt
import socketio

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
        user_name = uuid.uuid4()
        resp = requests.post("http://" + host + ":4000/auth/signup/",
                             {'name': user_name, 'role': 'user'})  # TODO : create user with role
        if resp.status_code == 201:
            # resp = requests.put("http://" + host + ":4000/auth/login/" + user_name)
            # resp = resp.json()
            decoded = jwt.decode(resp['jwt'], verify=False)
            user_id = decoded['user_id']
            access_token = decoded['access_token']
        else:
            print("Error with Login")

        self.socket.connect("http://" + host + ":5000/", headers={'user_id': user_id, 'access_token': access_token})
        print(str(self.id) + ": Connected")
        while True:
            self.socket.emit("message", {'user_id': user_id, 'access_token': access_token, 'client_id': self.id})
            time.sleep(random.randint(1, 3))


if __name__ == "__main__":
    numClients = 20
    host = '127.0.0.1'

    # print(jwt.decode(resp['jwt'], verify=False))

    # print(jwt.decode(resp['jwt']))
    thread = []
    for i in range(numClients):
        thread.append(Client(i, socketio.Client()))

    for t in thread:
        t.start()
