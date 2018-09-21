import assign from 'lodash/assign';
import * as actions from './actions';

const headers = {
  headers: {
    'Access-Control-Allow-Origin': '*',
    'Content-Type': 'application/json',
  },
};

const GET = assign({}, headers, { method: 'GET' });

function createRaces (races, dispatch) {
  dispatch(actions.createRaces(races));
}

export const fetchInitialData = () =>
  dispatch => fetch('../api/ap-election-meta/', GET)
    .then(response => response.json())
    .then(data => Promise.all([
      createRaces(data, dispatch)
    ])).catch((error) => {
      console.log('API Error fetchInitialData', error, error.code);
    });