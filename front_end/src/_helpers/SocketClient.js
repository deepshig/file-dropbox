import io from 'socket.io-client';
import store from '../_helpers/store'
import {storeSocketMessage} from "../_actions";

// Example conf. You can move this to your config file.
const host = 'http://localhost:4000/';
const socketPath = '/socket-io/';

export default class socketAPI {
    socket;

    connect() {
        this.socket = io.connect(host, {
            extraHeaders: {
                Authorization: "Bearer " + store.getState().authentication.token
            }
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
                this.socket.on('responseMessage', response => store.dispatch(storeSocketMessage(response['temperature'])));
                // console.log(store.getState().socketReducer.payload);

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