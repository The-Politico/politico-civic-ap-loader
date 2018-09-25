import assign from 'lodash/assign';

export default (currentState, action) => {
  const initialState = {
    lastActionType: null,
  };

  if (typeof currentState === 'undefined') {
    return initialState;
  }

  const newState = assign({}, currentState);
  newState.lastActionType = action.type;
  return newState;
};