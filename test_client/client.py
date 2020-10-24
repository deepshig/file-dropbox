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
global chunk_size
global frequency


class Client(threading.Thread):
    def __init__(self, id, socket):
        threading.Thread.__init__(self)
        self.id = id
        self.user_id = 0
        self.user_name = 0
        self.socket = socket
        self.file_id = 0
        self.f = open('out.npy', 'rb')
        self.f.seek(0, os.SEEK_END)
        self.file_size = self.f.tell()


        @socket.event
        def message(data):
            print(str(self.id) + ': Received data: ', data)

        @socket.on('start-transfer')
        def start_transfer(file_id):
            global chunk_size
            self.f.seek(0, os.SEEK_END)

            self.file_id = file_id['id']
            offset = 0
            while True:
                if offset < self.file_size:
                    self.f.seek(offset)

                    if chunk_size > self.file_size:
                        chunk_size = self.file_size

                    data = self.f.read(chunk_size-1) # TODO: Finalise and test this feature for larger files

                    self.socket.emit('write-chunk', data=(str(self.file_id), offset, data))
                    offset += chunk_size

                else:
                    print("Upload Complete")
                    self.socket.emit('complete-upload', data=(str(self.file_id), self.user_name, self.user_id))
                    break

        @socket.on('complete-upload')
        def complete_upload(resp):

            print("File uploaded: " + str(resp['data']))

    def run(self):
        self.user_name = "client" + str(self.id)

        resp = requests.put("http://" + host + ":4000/auth/login/" + self.user_name)  # TODO : create user with role

        if resp.status_code != 201:
            resp = requests.post("http://" + host + ":4000/auth/signup",
                                 {'name': self.user_name, 'role': 'user'})  # TODO : create user with role

        if resp.status_code == 201:

            resp = resp.json()
            decoded = jwt.decode(resp["jwt"], verify=False)
            self.user_id = decoded['user_id']
            access_token = decoded['access_token']
            self.socket.connect("http://" + host + ":5000/", headers={'user_id': self.user_id, 'access_token': access_token})
            print(str(self.id) + ": Connected")
            while True:
                self.socket.emit('start-transfer', data=(self.f.name, self.f.tell()))
                time.sleep(random.randint(frequency[0], frequency[1]))
        else:
            print("Error with Login")


if __name__ == "__main__":
    numClients = 5
    host = '127.0.0.1'
    chunk_size = 64 * 1024
    frequency = [1, 3]

    # print(jwt.decode(resp['jwt'], verify=False))

    # print(jwt.decode(resp['jwt']))
    thread = []
    for i in range(numClients):
        thread.append(Client(i, socketio.Client()))

    for t in thread:
        t.start()
