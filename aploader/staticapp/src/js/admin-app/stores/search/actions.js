import * as types from './constants';

export const selectState = state => ({
  type: types.SELECT_STATE,
  state,
});