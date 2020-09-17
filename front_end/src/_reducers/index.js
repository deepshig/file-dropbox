import {authentication} from './authentication.reducer'
import {combineReducers} from "redux";

const allReducers = combineReducers({
    authentication
});

export default allReducers