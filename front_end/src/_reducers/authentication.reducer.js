import { userConstants } from '../_constants/user.constants';

let user = '';
let token = '';
const initialState = {loggedIn: false, user, token};

export function authentication(state = initialState, action) {
    switch (action.type) {
        case userConstants.LOGIN_REQUEST:
            return {
                ...state,
                loggingIn: true,
                user: action.UID,
            };
        case userConstants.LOGIN_SUCCESS:
            return {
                ...state,
                loggedIn: true,
                user: action.UID,
                token: action.token
            };
        case userConstants.LOGIN_FAILURE:
            return {
                loggedIn: false,
            };
        case userConstants.LOGOUT:
            return {};
        default:
            return state
    }
}
