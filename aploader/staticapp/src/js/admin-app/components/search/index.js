import React, { Component } from 'react'
import Select from 'react-select'
import { states } from './utils';
import { fetchStateData } from '../../stores/races/api';

import './styles.scss';

class Search extends React.Component {
  constructor(props) {
    super(props);

    this.onChange = this.onChange.bind(this);
  }

  onChange(selection) {
    this.props.actions.selectState(selection.value);
  }

  render() {
    return(
      <div className='search'>
        <h2>Race calls</h2>
        <Select 
          options={states}
          onChange={this.onChange}
          placeholder='Select a state'
        />
      </div>
    )
  } 
}

export default Search;