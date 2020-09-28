import { socketConstants} from "../_constants/socket.constants";
import React from "react";


let status = 'disconnected';
const initialState = {status};

export function socketReducer(state = initialState, action) {
    switch (action.type) {
        case socketConstants.SOCKET_REQUEST:
            return {
                status: 'connected',
                payload: action.payload,
            };
        case socketConstants.SOCKET_FAILURE:
            return {
                status: 'failed',
            };
        case socketConstants.SOCKET_REMOVE:
            return {
                status: 'disconnected',
            };
        default:
            return state
    }
}
