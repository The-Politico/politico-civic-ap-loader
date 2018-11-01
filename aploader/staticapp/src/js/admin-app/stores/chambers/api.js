import assign from 'lodash/assign';
import * as actions from './actions';

const headers = {
  headers: {
    'Access-Control-Allow-Origin': '*',
    'Content-Type': 'application/json',
  },
};

const GET = assign({}, headers, { method: 'GET' });

function addChamberCalls (calls, dispatch) {
  dispatch(actions.setChamberCalls(calls));
}

export const fetchChamberCalls = () =>
  dispatch => fetch('../api/chamber-calls/', GET)
    .then(response => response.json())
    .then(data => Promise.all([
      addChamberCalls(data, dispatch)
    ])).catch((error) => {
      console.log('API Error fetchInitialData', error, error.code);
    });