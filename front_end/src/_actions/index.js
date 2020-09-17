import {userConstants} from "../_constants/user.constants";

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