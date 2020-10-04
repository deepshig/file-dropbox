import io from 'socket.io-client';
import store from '../_helpers/store'
import {storeSocketMessage, successSocket, failedSocket} from "../_actions";

// Example conf. You can move this to your config file.
const host = 'http://localhost:5000/';
const socketPath = '/socket-io/';

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
                this.socket.on('message', response => store.dispatch(storeSocketMessage(response['data'])));
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
}