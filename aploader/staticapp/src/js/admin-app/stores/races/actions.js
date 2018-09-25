import * as types from './constants';

export const createRaces = races => ({
  type: types.CREATE_RACES,
  races,
});

export const setCandidateWinner = (raceID, candidateID) => ({
  type: types.SET_CANDIDATE_WINNER,
  raceID,
  candidateID,
});

export const setCandidateLoser = (raceID, candidateID) => ({
  type: types.SET_CANDIDATE_LOSER,
  raceID,
  candidateID,
});

export const setAllCandidatesToLoser = raceID => ({
  type: types.SET_ALL_CANDIDATES_TO_LOSER,
  raceID,
})

export const setRaceOverride = raceID => ({
  type: types.SET_RACE_OVERRIDE,
  raceID,
});

export const removeRaceOverride = raceID => ({
  type: types.REMOVE_RACE_OVERRIDE,
  raceID,
});

export const setRaceAPCalled = raceID => ({
  type: types.SET_RACE_AP_CALLED,
  raceID,
});

export const removeRaceAPCalled = raceID => ({
  type: types.REMOVE_RACE_AP_CALLED,
  raceID,
});