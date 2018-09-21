import React from 'react';
import { render } from 'react-dom';
import { Provider } from 'react-redux';
import App from './admin-app/components/App';
import store from './admin-app/stores/';

const AdminApp = () => (
  <Provider store={store}>
    <App />
  </Provider>
)
 

render(
  <AdminApp />, 
  document.getElementById('app')
);
