import * as types from './constants';

export const setChamberCalls = calls => ({
  type: types.SET_CHAMBER_CALLS,
  calls,
});

export const changeChamberCall = (call, party) => ({
  type: types.CHANGE_CHAMBER_CALL,
  call,
  party
});
