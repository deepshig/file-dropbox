import io from 'socket.io-client';
import store from '../_helpers/store'

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

            return this.socket.emit(event, data, (response) => {
                return resolve();
            });
        });
    }

    on(event, fun) {
        // No promise is needed here, but we're expecting one in the middleware.
        return new Promise((resolve, reject) => {
            if (!this.socket) return reject('No socket connection.');

            this.socket.on(event, fun);
            resolve();
        });
    }
}