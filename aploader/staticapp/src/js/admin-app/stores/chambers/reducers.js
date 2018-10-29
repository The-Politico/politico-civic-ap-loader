import assign from 'lodash/assign';
import sortBy from 'lodash/sortBy';
import * as types from './constants';

export default(currentState, action) => {
  const initialState = [];

  if (typeof currentState === 'undefined') {
    return initialState;
  }

  const copy = currentState.slice();

  switch(action.type) {
    case types.SET_CHAMBER_CALLS:
      return action.calls;
    case types.CHANGE_CHAMBER_CALL:
      call = copy.find(c => c.body === action.call.body)
      call.party = action.call.party
      return copy;
    default:
      break;
  }

  return currentState;
}
