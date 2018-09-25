import { applyMiddleware, combineReducers, compose, createStore } from 'redux';
import thunkMiddleware from 'redux-thunk';
import meta from './meta/reducers';
import races from './races/reducers';
import search from './search/reducers';
import { fetchStateData } from './races/api';

const reducers = combineReducers({
  meta,
  races,
  search,
});

const store = createStore(reducers, compose(
  applyMiddleware(thunkMiddleware),
  window.devToolsExtension ? window.devToolsExtension() : f => f,
));

store.subscribe(() => {
  const state = store.getState();

  if (!state.meta) {
    return;
  }

  if (state.meta.lastActionType === 'SELECT_STATE') {
    store.dispatch(fetchStateData(state.search.state));
  }
})

export default store;