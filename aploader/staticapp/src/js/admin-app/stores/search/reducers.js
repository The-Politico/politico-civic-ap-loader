import assign from 'lodash/assign';
import * as types from './constants';

export default(currentState, action) => {
  const initialState = {
    state: '',
  };

  if (typeof currentState === 'undefined') {
    return initialState;
  }

  switch(action.type) {
    case types.SELECT_STATE:
      return assign({}, currentState, {
        state: action.state
      });
    default:
      break;
  }


  return currentState;
}