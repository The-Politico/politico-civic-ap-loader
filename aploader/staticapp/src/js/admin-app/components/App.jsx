import React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { getRacesByBody } from '../stores/races/reducers';
import { Sketch } from 'politico-style';
import Race from './race';

const { Nav } = Sketch;

class App extends React.Component {
  render () {
    return (
      <div>
        <Nav
          appName='Race calls'
          homeLink='civic.politicoapps.com'
          appLink='civic.politicoapps.com'
        />
        <div className='container'>
          <div className='races'>
            {this.props.races.map(race => (
              <Race race={race} key={race.ap_election_id} />
            ))}
          </div>
        </div>
      </div>
    );
  }
}

const mapStateToProps = state => {
  return {
    races: getRacesByBody(state.races, 'house'),
  }
};

export default connect(mapStateToProps)(App);
