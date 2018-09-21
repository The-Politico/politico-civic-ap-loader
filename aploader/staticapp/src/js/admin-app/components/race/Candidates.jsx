import React from 'react';
import { Sketch } from 'politico-style';
import sortBy from 'lodash/sortBy';

const { Button } = Sketch;

class Candidates extends React.Component {
  constructor(props) {
    super(props);

    this.onCallClick = this.onCallClick.bind(this);
  }

  onCallClick(e) {
    console.log(e.target);
  }

  render() {
    const { candidates } = this.props;
    const sorted = sortBy(candidates, c => c.votes.count).reverse();

    return (
      <table className='candidates table'>
        <thead>
          <tr>
            <th>Candidate</th>
            <th>Party</th>
            <th>Vote %</th>
            <th>AP Call</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {sorted.map(c => (
            <tr className={`candidate ${c.votes.winning ? 'winner' : ''}`}>
              <td>{c.name}</td>
              <td>{c.party}</td>
              <td>{Math.round(c.votes.pct * 100)}%</td>
              <td>{c.votes.winning ? 'Winner' : ''}</td>
              <td>
                <Button 
                  outline
                  onClick={this.onCallClick}
                >
                  {c.votes.winning ? 'Remove call' : 'Call winner'}
                </Button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    )
  }
}

export default Candidates;
