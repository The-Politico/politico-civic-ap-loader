import React from 'react';
import { Sketch } from 'politico-style';
import Cookies from 'js-cookie';
const { Button } = Sketch;

const headers = {
  'Access-Control-Allow-Origin': '*',
  'Content-Type': 'application/json',
  'X-CSRFToken': Cookies.get('csrftoken'),
};

function determineButtonAction(candidate, called, overriding) {
  const winning = candidate.votes.winning;

  let buttonAction = '';
  if (winning && called && overriding) {
    buttonAction = 'Accept AP Call';
  } else if (winning && called && !overriding) {
    buttonAction = 'Override AP Call';
  } else if (winning && !called) {
    buttonAction = 'Remove call';
  } else if (!winning) {
    buttonAction = 'Call winner';
  }

  return buttonAction;
}

class Candidate extends React.Component {
  constructor(props) {
    super(props);
    const { c, called, overriding } = this.props;
    const buttonAction = determineButtonAction(c, called, overriding);

    this.state = {
      buttonAction,
    }
    
    this.onCallClick = this.onCallClick.bind(this);
  }

  static getDerivedStateFromProps(props, state) {
    const { c, called, overriding } = props;

    const buttonAction = determineButtonAction(c, called, overriding);

    return {buttonAction}
  }

  onCallClick(e) {
    const { actions, electionID, c } = this.props;
    const { buttonAction } = this.state;

    const postBody = {
      ap_election_id: electionID,
      ap_candidate_id: c.ap_candidate_id,
    }


    if (buttonAction === 'Accept AP Call') {
      postBody['override'] = false;
    }

    if (buttonAction === 'Override AP Call') {
      postBody['override'] = true;
    }

    if (buttonAction === 'Remove call') {
      postBody['override'] = false;
      postBody['winner'] = false;
    }

    if (buttonAction === 'Call winner') {
      postBody['override'] = true;
      postBody['winner'] = true;
      postBody['called'] = false;
    }

    fetch(`../api/ap-election-meta/${state}/`, {
      method: 'POST',
      headers,
      body: JSON.stringify(postBody)
    }).then(response => response.json()).then(data => {
      if (buttonAction === 'Accept AP Call') {
        actions.removeRaceOverride(electionID);
      }

      if (buttonAction === 'Override AP Call') {
        actions.setRaceOverride(electionID);
      }

      if (buttonAction === 'Remove call') {
        actions.removeRaceOverride(electionID);
        actions.setCandidateLoser(electionID, c.ap_candidate_id);
      }

      if (buttonAction === 'Call winner') {
        actions.setRaceOverride(electionID);
        actions.setAllCandidatesToLoser(electionID);
        actions.setCandidateWinner(electionID, c.ap_candidate_id);
        actions.removeRaceAPCalled(electionID);
      }
    }).catch(err => console.error(err));
  }

  render() {
    const { c, called, overriding } = this.props;
    const { buttonAction } = this.state;

    return (
      <tr key={c.name} className={`candidate ${c.votes.winning ? 'winner' : ''}`}>
        <td>{c.name}</td>
        <td>{c.party}</td>
        <td>{Math.round(c.votes.pct * 100)}%</td>
        <td>
          {c.votes.winning && called && 'AP '}
          {c.votes.winning && !called && 'POLITICO '}
          {c.votes.winning ? 'Winner' : ''}
        </td>
        <td>
          <Button 
            outline
            onClick={this.onCallClick}
          >
            {buttonAction}
          </Button>
        </td>
      </tr>
    );
  }
}

export default Candidate;
