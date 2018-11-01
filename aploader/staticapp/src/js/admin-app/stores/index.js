import { applyMiddleware, combineReducers, compose, createStore } from 'redux';
import thunkMiddleware from 'redux-thunk';
import chamberCalls from './chambers/reducers';
import meta from './meta/reducers';
import races from './races/reducers';
import search from './search/reducers';

import { fetchChamberCalls } from './chambers/api';
import { fetchStateData } from './races/api';

const reducers = combineReducers({
  chamberCalls,
  meta,
  races,
  search,
});

const store = createStore(reducers, compose(
  applyMiddleware(thunkMiddleware),
  window.devToolsExtension ? window.devToolsExtension() : f => f,
));

store.dispatch(fetchChamberCalls());

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
