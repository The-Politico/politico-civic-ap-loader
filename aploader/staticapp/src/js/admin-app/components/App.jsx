import React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { getRaces } from '../stores/races/reducers';
import { Sketch } from 'politico-style';
import Search from './search';
import Race from './race';
import * as raceActions from '../stores/races/actions';
import * as searchActions from '../stores/search/actions';
import assign from 'lodash/assign';

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
          <div className='search'>
            <Search actions={this.props.actions}/>
          </div>
          <div className='races'>
            {this.props.races.map(race => (
              <Race 
                race={race}
                key={race.ap_election_id} 
                actions={this.props.actions}
                state={this.props.state}
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
    state: state.search.state,
  }
};

const mapDispatchToProps = dispatch => ({
  actions: bindActionCreators(assign({}, raceActions, searchActions), dispatch),
});

export default connect(mapStateToProps, mapDispatchToProps)(App);
