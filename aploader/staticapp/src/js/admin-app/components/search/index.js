import React, { Component } from 'react'
import Select from 'react-select'
import { states } from './utils';

import './styles.scss';

class Search extends React.Component {
  constructor(props) {
    super(props);

    this.onChange = this.onChange.bind(this);
  }

  onChange(selection) {
    console.log(this.props.actions);
    this.props.actions.selectState(selection.value);
  }

  render() {
    return(
      <Select 
        options={states}
        onChange={this.onChange}
        placeholder='Select a state'
      />
    )
  } 
}

export default Search;