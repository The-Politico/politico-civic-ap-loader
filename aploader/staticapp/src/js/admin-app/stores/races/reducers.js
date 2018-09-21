import assign from 'lodash/assign';
import sortBy from 'lodash/sortBy';
import * as types from './constants';

export default(currentState, action) => {
  const initialState = [];

  if (typeof currentState === 'undefined') {
    return initialState;
  }

  switch(action.type) {
    case types.CREATE_RACES:
      return action.races;
    default:
      break;
  }

  return currentState;
}

export const getRacesByBody = (races, body) =>
  sortBy(races.filter(r => r.election.body === body), r => r.election.office);