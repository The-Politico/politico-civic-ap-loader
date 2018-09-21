import { applyMiddleware, combineReducers, compose, createStore } from 'redux';
import thunkMiddleware from 'redux-thunk';
import races from './races/reducers';
import { fetchInitialData } from './races/api';

const reducers = combineReducers({
  races,
});

const store = createStore(reducers, compose(
  applyMiddleware(thunkMiddleware),
  window.devToolsExtension ? window.devToolsExtension() : f => f,
));

store.dispatch(fetchInitialData());

export default store;