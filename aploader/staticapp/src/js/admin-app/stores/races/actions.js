import * as types from './constants';

export const createRaces = races => ({
  type: types.CREATE_RACES,
  races,
});