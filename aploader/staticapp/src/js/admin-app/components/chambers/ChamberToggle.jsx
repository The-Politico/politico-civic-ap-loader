import React from 'react';
import Cookies from 'js-cookie';
import TriToggle from 'react-posed-tritoggle';
import { Sketch } from 'politico-style';
const { Button } = Sketch;

const headers = {
  'Access-Control-Allow-Origin': '*',
  'Content-Type': 'application/json',
  'X-CSRFToken': Cookies.get('csrftoken'),
};

class ChamberToggle extends React.Component {
  constructor(props) {
    super(props);
    let startingValue = 1;

    if (props.call.party === 'Dem') {
      startingValue = 0;
    } else if (props.call.party === 'GOP') {
      startingValue = 2;
    }

    this.state = {
      serverValue: startingValue,
      value: startingValue,
      changed: false
    };

    this.onClick = this.onClick.bind(this);
  }

  partyToValue(party) {
    if (!party) return 1;
    if (party === 'Dem') return 0;
    if (party === 'GOP') return 2;
  }

  valueToParty(value) {
    if (value === 0) return 'Dem';
    if (value === 1) return null;
    if (value === 2) return 'GOP';
  }

  onClick() {
    const postBody = {
      body: this.props.call.body,
      party: this.valueToParty(this.state.value),
    };

    fetch(`../api/chamber-calls/`, {
      method: 'POST',
      headers,
      body: JSON.stringify(postBody)
  }).then(response => response.json()).then(data => {
    this.setState({
      serverValue: this.state.value,
    })
  })
}

  render() {
    return (
      <div className='chamber-toggle'>
        <div className='toggle'>
          <h5>{this.props.call.body}</h5>
          <TriToggle
            width={110}
            value={this.state.value}
            labels={['Dem', 'GOP']}
            onChange={(value) => {
              this.setState({ value, changed: value !== this.state.serverValue })
            }}
          />
        </div>
        <div className='save'>
          {this.state.changed ? (
            <Button 
              outline
              onClick={this.onClick}
            >
            Save call
            </Button>
          ): (
            <button className='btn btn-outline-secondary' disabled>Save call</button>
          )}
        </div>
      </div>
    );
  }
}

export default ChamberToggle;
