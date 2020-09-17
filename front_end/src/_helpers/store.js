import { createStore, applyMiddleware } from 'redux';
import thunkMiddleware from 'redux-thunk';
import allReducers from '../_reducers';
import { composeWithDevTools } from 'redux-devtools-extension';

const store = createStore(allReducers,
    composeWithDevTools(
        applyMiddleware(
        thunkMiddleware),
    ));
export default store