import { socketConstants} from "../_constants/socket.constants";
import React from "react";


let status = 'disconnected';
let payload = 'nothing';
const initialState = {status, payload};

export function socketReducer(state = initialState, action) {
    switch (action.type) {
        case socketConstants.SOCKET_REQUEST:
            return {
                status: 'connecting',
                payload: action.payload,
            };
        case socketConstants.SOCKET_SUCCESS:
            return {
                status: 'connected',
                host: action.payload,
            };
        case socketConstants.SOCKET_FAILURE:
            return {
                status: 'failed',
            };
        case socketConstants.SOCKET_DISCONNECT:
            return {
                status: 'disconnected',
            };
        case socketConstants.SOCKET_MESSAGE_STORE:
            console.log(action.payload);
            return{
                ...state,
                payload: action.payload
            };
        default:
            return state
    }
}
