import React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { getRaces } from '../stores/races/reducers';
import { Sketch } from 'politico-style';
import Race from './race';
import * as actions from '../stores/races/actions';

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
              <Race 
                race={race}
                key={race.ap_election_id} 
                actions={this.props.actions}
              />
            ))}
          </div>
        </div>
      </div>
    );
  }
}

const mapStateToProps = state => {
  return {
    races: getRaces(state.races),
  }
};

const mapDispatchToProps = dispatch => ({
  actions: bindActionCreators(actions, dispatch),
});

export default connect(mapStateToProps, mapDispatchToProps)(App);
