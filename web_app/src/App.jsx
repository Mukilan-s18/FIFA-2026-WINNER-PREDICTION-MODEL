import { useEffect, useState } from 'react';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import PowerRankings from './components/PowerRankings';
import Spotlight from './components/Spotlight';
import TournamentProbabilities from './components/TournamentProbabilities';

function App() {
  const [data, setData] = useState([]);

  useEffect(() => {
    fetch('/data.json')
      .then(res => res.json())
      .then(setData)
      .catch(console.error);
  }, []);

  if (!data.length) {
    return <div className="flex items-center justify-center" style={{height: '100vh'}}>Loading Data...</div>;
  }

  // Find the top team for the hero
  const sortedData = [...data].sort((a, b) => b.win_prob - a.win_prob);
  const topTeam = sortedData[0];
  
  // Find Portugal for the spotlight
  const portugalData = data.find(team => team.team === 'Portugal') || sortedData[1];

  return (
    <div className="app-container">
      <Navbar />
      <Hero topTeam={topTeam} />
      
      <div className="grid grid-cols-2 gap-8" style={{ marginTop: '2rem', paddingBottom: '4rem' }}>
        <PowerRankings data={sortedData} />
        <div className="flex-col gap-8">
          <Spotlight teamData={portugalData} />
          <TournamentProbabilities data={sortedData} />
        </div>
      </div>
    </div>
  );
}

export default App;
