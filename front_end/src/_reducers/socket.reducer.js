import { socketConstants} from "../_constants/socket.constants";

let status = 'disconnected';
const initialState = {status};

export function socketReducer(state = initialState, action) {
    switch (action.type) {
        case socketConstants.SOCKET_REQUEST:
            return {
                status: 'connecting',
            };
        case socketConstants.SOCKET_SUCCESS:
            return {
                status: 'connected',
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
