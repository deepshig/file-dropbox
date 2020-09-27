import {userConstants} from "../_constants/user.constants";
import {socketConstants} from "../_constants/socket.constants";

export const callLogin = (UID) => {
    return{
        type: userConstants.LOGIN_REQUEST,
        UID: UID,
    }
}
export const setLogin = (UID, token) => {
    return{
        type: userConstants.LOGIN_SUCCESS,
        UID: UID,
        token: token
    }
}
export const createSocket = () => {
    return{
        type: socketConstants.SOCKET_REQUEST,
    }
}