import assign from 'lodash/assign';
import sortBy from 'lodash/sortBy';
import * as types from './constants';

export default(currentState, action) => {
  const initialState = [];

  if (typeof currentState === 'undefined') {
    return initialState;
  }

  const copy = currentState.slice();
  const race = copy.find(r => r.ap_election_id === action.raceID);

  switch(action.type) {
    case types.CREATE_RACES:
      return action.races;
    case types.SET_CANDIDATE_WINNER:
      const winner = race.election.candidates.find(c => 
        c.ap_candidate_id === action.candidateID);
      winner.votes.winning = true;
      return copy;
    case types.SET_CANDIDATE_LOSER:
      const loser = race.election.candidates.find(c => 
        c.ap_candidate_id === action.candidateID);
      loser.votes.winning = false;
      return copy;
    case types.SET_ALL_CANDIDATES_TO_LOSER:
      race.election.candidates.forEach(c => c.votes.winning = false);
      return copy;
    case types.SET_RACE_OVERRIDE:
      race.override_ap_call = true;
      return copy;
    case types.REMOVE_RACE_OVERRIDE:
      race.override_ap_call = false;
      return copy;
    case types.SET_RACE_AP_CALLED:
      race.called = true;
      return copy;
    case types.REMOVE_RACE_AP_CALLED:
      race.called = false;
      return copy;

    default:
      break;
  }

  return currentState;
}

export const getRaces = (races) => sortBy(races, r => r.election.office);