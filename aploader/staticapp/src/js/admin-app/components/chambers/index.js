import React from 'react';
import ChamberToggle from './ChamberToggle';

class Chambers extends React.Component {
  render() {
    return (
      <div className='chambers'>
        <h2>Chamber calls</h2>
        <div className='toggles'>
          {this.props.chamberCalls.map(call => (
            <ChamberToggle key={call.body} call={call} />
          ))}
        </div>
      </div>
    );
  }
}

export default Chambers;
