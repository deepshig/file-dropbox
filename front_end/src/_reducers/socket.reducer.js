import { socketConstants} from "../_constants/socket.constants";
import React from "react";


let status = 'disconnected';
let payload = 'Not Connected';
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
                payload: 'Connected',
                host: action.payload,
            };
        case socketConstants.SOCKET_FAILURE:
            return {
                status: 'failed',
                payload: 'Failed',

            };
        case socketConstants.SOCKET_DISCONNECT:
            return {
                status: 'disconnected',
            };
        case socketConstants.SOCKET_MESSAGE_STORE:
            return{
                ...state,
                payload: action.payload
            };
        default:
            return state
    }
}
