import React from 'react';
import sortBy from 'lodash/sortBy';
import Candidate from './Candidate';


class Candidates extends React.Component {
  render() {
    const { candidates, electionID, actions, called, overriding, state } = this.props;
    const sorted = sortBy(candidates, c => c.votes.count).reverse();

    return (
      <table className='candidates table'>
        <thead>
          <tr>
            <th>Candidate</th>
            <th>Party</th>
            <th>Vote %</th>
            <th>Call</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {sorted.map(c => (
            <Candidate 
              key={c.name}
              c={c}
              electionID={electionID}
              actions={actions}
              called={called}
              overriding={overriding}
              state={state}
            />
          ))}
        </tbody>
      </table>
    )
  }
}

export default Candidates;
