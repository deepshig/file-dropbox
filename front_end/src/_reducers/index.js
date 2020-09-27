import {authentication} from './authentication.reducer'
import {socketReducer} from "./socket.reducer";
import {combineReducers} from "redux";

const allReducers = combineReducers({
    authentication,
    socketReducer
});

export default allReducers