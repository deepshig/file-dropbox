import io from 'socket.io-client';
import store from '../_helpers/store'
import {storeSocketMessage, successSocket, failedSocket} from "../_actions";

// Example conf. You can move this to your config file.
// const host = 'http://54.154.129.30:5000/';
const host = 'http://54.170.85.210:5000/';
const socketPath = '/socket-io/';
const chunk_size = 64 * 1024;

export default class socketAPI {
    socket;


    connect() {
        // this.socket = io(host);
        // // this.data = {query: {token: store.getState().authentication.token, uid: store.getState().authentication.user};
        // this.socket.on('connect', function(data){
        //     // {query: {token: store.getState().authentication.token, uid: store.getState().authentication.user}}
        //
        //         console.log("heloo")
        //     }
        // );

        let reattempts = 2;

        this.socket = io.connect(host, {
            secure: true,
            query: {token: store.getState().authentication.token, uid: store.getState().authentication.user},
            reconnection: true,
            reconnectionDelay: 1000,
            reconnectionDelayMax : 5000,
            reconnectionAttempts: reattempts

        });
        this.socket.on('connect_error', function() {
            reattempts = reattempts - 1;
            if (reattempts === 0){
                store.dispatch(failedSocket());
            }
        });
    }

    connected() {
        return new Promise((resolve, reject) => {
            if (!this.socket) return reject('No socket connection.');

            this.socket.on('alive', (response) => {if(response['alive']) {store.dispatch(successSocket(host))}});

            return this.socket.emit("alive", {
                User: store.getState().authentication.user
            }, response => {
                return resolve();
            });

        });
    }

    disconnect() {
        return new Promise((resolve) => {
            this.socket.disconnect(() => {
                this.socket = null;
                resolve();
            });
        });
    }

    send(event, data) {
        return new Promise((resolve, reject) => {
            if (!this.socket) return reject('No socket connection.');

            return this.socket.emit(event, data,{
                extraHeaders: {
                    Authorization: "Bearer " + store.getState().authentication.token
                }
            }, response => {
                this.socket.on(event, response => store.dispatch(storeSocketMessage(response['data'])));
                console.log(store.getState().socketReducer.payload);

                return resolve();
            });
        });
    }

    on(event, fun) {
        // No promise is needed here, but we're expecting one in the middleware.
        return new Promise((resolve, reject) => {
            if (!this.socket) return reject('No socket connection.');

            this.socket.on(event, (response) =>{
                store.dispatch(storeSocketMessage(response['data'])); console.log(response['data'])});
            return resolve();
        });
    }

    onReadSuccess(file, offset, length, data) {
        if (this.done) {
            this.socket.emit('complete-upload', file.name, response => {
                this.socket.on('complete-upload', response => console.log(response['data']));
            });
            return;
        }
        this.socket.emit('write-chunk', file.name, offset, data, function(offset, ack) {
            if (!ack)
                this.onReadError(file, offset, 0, 'Transfer aborted by server')
        }.bind(this, offset));
        let end_offset = offset + length;
        if (end_offset < file.size)
            this.readFileChunk(file, end_offset, chunk_size,
                this.onReadSuccess.bind(this),
                this.onReadError.bind(this));
        else {
            this.done = true;
        }
    }

    onReadError(file, offset, length, error) {
        console.log('Upload error for ' + file.name + ': ' + error);
        this.done = true;
    }

    readFileChunk(file, offset) {
        return new Promise((resolve, reject) => {
            if (!this.socket) return reject('No socket connection.');

            let success = this.onReadSuccess.bind(this);
            let error = this.onReadError.bind(this);

            let end_offset = offset + chunk_size;
            if (end_offset > file.size)
                end_offset = file.size;
            var r = new FileReader();
            r.onload = function (file, offset, chunk_size, e) {
                if (e.target.error != null)
                    error(file, offset, chunk_size, e.target.error);
                else
                    success(file, offset, chunk_size, e.target.result);
            }.bind(r, file, offset, chunk_size);
            r.readAsArrayBuffer(file.slice(offset, end_offset));
        });
    }

}