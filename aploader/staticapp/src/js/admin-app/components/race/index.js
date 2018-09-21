import React from 'react';
import Candidates from './Candidates';
import './styles.scss';

class Race extends React.Component {
  render() {
    const { race } = this.props;

    return (
      <div className='race'>
        <h3>{race.election.office}</h3>
        <Candidates candidates={race.election.candidates} />
      </div>
    )
  }
}

export default Race;
