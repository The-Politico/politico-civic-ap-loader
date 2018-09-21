import React from 'react';
import { Sketch } from 'politico-style';
import sortBy from 'lodash/sortBy';

const { Button } = Sketch;

class Candidates extends React.Component {
  render() {
    const { candidates } = this.props;
    const sorted = sortBy(candidates, c => c.votes.count).reverse();

    return (
      <table className='candidates table'>
        <tbody>
          {sorted.map(c => (
            <tr className='candidate'>
              <td>{c.name}</td>
              <td>{c.party}</td>
              <td>{Math.round(c.votes.pct * 100)}%</td>
              <td>{c.votes.winning ? 'Winner' : <Button outline>Call winner</Button>}</td>
            </tr>
          ))}
        </tbody>
      </table>
    )
  }
}

export default Candidates;
