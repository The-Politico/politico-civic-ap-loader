import assign from 'lodash/assign';
import * as actions from './actions';

const headers = {
  headers: {
    'Access-Control-Allow-Origin': '*',
    'Content-Type': 'application/json',
  },
};

function getParameterByName(name, url) {
  if (!url) url = window.location.href;
  name = name.replace(/[\[\]]/g, '\\$&');
  var regex = new RegExp('[?&]' + name + '(=([^&#]*)|&|#|$)'),
      results = regex.exec(url);
  if (!results) return null;
  if (!results[2]) return '';
  return decodeURIComponent(results[2].replace(/\+/g, ' '));
}

const GET = assign({}, headers, { method: 'GET' });

function createRaces (races, dispatch) {
  dispatch(actions.createRaces(races));
}

export const fetchInitialData = () =>
  dispatch => fetch(`../api/ap-election-meta/${getParameterByName('state')}`, GET)
    .then(response => response.json())
    .then(data => Promise.all([
      createRaces(data, dispatch)
    ])).catch((error) => {
      console.log('API Error fetchInitialData', error, error.code);
    });