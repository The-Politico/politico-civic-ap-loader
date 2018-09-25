import { applyMiddleware, combineReducers, compose, createStore } from 'redux';
import thunkMiddleware from 'redux-thunk';
import races from './races/reducers';
import search from './search/reducers';
import { fetchStateData } from './races/api';

const reducers = combineReducers({
  races,
  search,
});

const store = createStore(reducers, compose(
  applyMiddleware(thunkMiddleware),
  window.devToolsExtension ? window.devToolsExtension() : f => f,
));

// store.dispatch(fetchInitialData());

store.subscribe(() => {
  const state = store.getState();
  if (!state.search.state) {
    return;
  }

  store.dispatch(fetchStateData(state.search.state));
})

export default store;