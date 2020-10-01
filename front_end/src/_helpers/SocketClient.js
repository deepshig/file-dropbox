import io from 'socket.io-client';
import store from '../_helpers/store'
import {storeSocketMessage} from "../_actions";

// Example conf. You can move this to your config file.
const host = 'http://localhost:50000/';
const socketPath = '/socket-io/';

export default class socketAPI {
    socket;

    connect() {
        // this.socket = io(host);
        // this.socket.on('connect',{
        //         query: {token: store.getState().authentication.token, uid: store.getState().authentication.user}
        //     }, function () {
        //         console.log("heloo");
        //     // socket connected
        // });

        this.socket = io.connect(host, {
            query: {token: store.getState().authentication.token, uid: store.getState().authentication.user}
        }, function(){
            console.log("heloo");
        });
    }

    connected() {
        return new Promise((resolve, reject) => {
            if (!this.socket) return reject('No socket connection.');
            console.log(this.socket.connected);

            return resolve();

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

            this.socket.on(event, (response) =>
            console.log(response));
            resolve();
        });
    }
}