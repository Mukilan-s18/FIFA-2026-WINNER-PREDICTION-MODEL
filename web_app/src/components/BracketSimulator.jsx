import { useState, useEffect } from 'react';
import confetti from 'canvas-confetti';

const getCountryCode = (teamName) => {
  const map = {
    'Spain': 'es', 'Serbia': 'rs', 'Argentina': 'ar', 'Peru': 'pe',
    'France': 'fr', 'Egypt': 'eg', 'England': 'gb-eng', 'United States': 'us',
    'Brazil': 'br', 'Scotland': 'gb-sct', 'Portugal': 'pt', 'Australia': 'au',
    'Netherlands': 'nl', 'South Korea': 'kr', 'Germany': 'de', 'Paraguay': 'py',
    'Colombia': 'co', 'Iran': 'ir', 'Croatia': 'hr', 'Canada': 'ca',
    'Morocco': 'ma', 'Nigeria': 'ng', 'Italy': 'it', 'Senegal': 'sn',
    'Japan': 'jp', 'Turkey': 'tr', 'Ecuador': 'ec', 'Denmark': 'dk',
    'Uruguay': 'uy', 'Switzerland': 'ch', 'Belgium': 'be', 'Mexico': 'mx',
    'Ivory Coast': 'ci', 'Uzbekistan': 'uz', 'Panama': 'pa', 'Poland': 'pl',
    'Honduras': 'hn', 'Tunisia': 'tn', 'Albania': 'al', 'Cameroon': 'cm'
  };
  return map[teamName] || null;
};

export default function BracketSimulator({ data }) {
  const [bracket, setBracket] = useState(null);
  const [isSimulating, setIsSimulating] = useState(false);

  useEffect(() => {
    if (data && data.length >= 32) {
      const top32 = data.slice(0, 32);
      const roundOf32 = [];
      for (let i = 0; i < 16; i++) {
        roundOf32.push([top32[i], top32[31 - i]]);
      }
      setBracket({
        r32: roundOf32,
        r16: Array(8).fill([null, null]),
        qf: Array(4).fill([null, null]),
        sf: Array(2).fill([null, null]),
        final: [[null, null]],
        winner: null
      });
    }
  }, [data]);

  const delay = ms => new Promise(res => setTimeout(res, ms));

  const simulateMatch = (teamA, teamB) => {
    if (!teamA) return teamB;
    if (!teamB) return teamA;
    return teamA.win_prob >= teamB.win_prob ? teamA : teamB;
  };

  const simulateRound = (currentRoundMatches) => {
    const winners = currentRoundMatches.map(match => simulateMatch(match[0], match[1]));
    const nextRoundMatches = [];
    for (let i = 0; i < winners.length; i += 2) {
      nextRoundMatches.push([winners[i], winners[i+1]]);
    }
    return { winners, nextRoundMatches };
  };

  const startSimulation = async () => {
    if (!data || data.length < 32 || isSimulating) return;
    setIsSimulating(true);

    const top32 = data.slice(0, 32);
    const roundOf32 = [];
    for (let i = 0; i < 16; i++) {
      roundOf32.push([top32[i], top32[31 - i]]);
    }
    
    let currentBracket = {
      r32: roundOf32,
      r16: Array(8).fill([null, null]),
      qf: Array(4).fill([null, null]),
      sf: Array(2).fill([null, null]),
      final: [[null, null]],
      winner: null
    };
    
    setBracket(currentBracket);
    await delay(500);

    const { nextRoundMatches: r16 } = simulateRound(currentBracket.r32);
    currentBracket = { ...currentBracket, r16 };
    setBracket(currentBracket);
    await delay(800);

    const { nextRoundMatches: qf } = simulateRound(currentBracket.r16);
    currentBracket = { ...currentBracket, qf };
    setBracket(currentBracket);
    await delay(800);

    const { nextRoundMatches: sf } = simulateRound(currentBracket.qf);
    currentBracket = { ...currentBracket, sf };
    setBracket(currentBracket);
    await delay(800);

    const { nextRoundMatches: final } = simulateRound(currentBracket.sf);
    currentBracket = { ...currentBracket, final };
    setBracket(currentBracket);
    await delay(1200);

    const { winners: winner } = simulateRound(currentBracket.final);
    currentBracket = { ...currentBracket, winner: winner[0] };
    setBracket(currentBracket);
    
    setIsSimulating(false);
    
    // Trigger celebratory confetti for the winner
    const duration = 3500;
    const end = Date.now() + duration;

    (function frame() {
      confetti({
        particleCount: 5,
        angle: 60,
        spread: 55,
        origin: { x: 0 },
        colors: ['#FFD700', '#ffffff', '#111111'],
        zIndex: 9999
      });
      confetti({
        particleCount: 5,
        angle: 120,
        spread: 55,
        origin: { x: 1 },
        colors: ['#FFD700', '#ffffff', '#111111'],
        zIndex: 9999
      });

      if (Date.now() < end) {
        requestAnimationFrame(frame);
      }
    }());
  };

  if (!bracket) return null;

  const Match = ({ match }) => {
    const codeA = match[0] ? getCountryCode(match[0].team) : null;
    const codeB = match[1] ? getCountryCode(match[1].team) : null;

    return (
      <div style={{
        display: 'flex', flexDirection: 'column',
        background: 'rgba(255,255,255,0.03)', border: '1px solid var(--glass-border-light)',
        borderRadius: '6px', overflow: 'hidden', width: '110px', margin: '3px 0', zIndex: 2, position: 'relative'
      }}>
        <div style={{ padding: '5px 6px', borderBottom: '1px solid rgba(255,255,255,0.05)', fontSize: '0.75rem', fontWeight: 600, color: match[0] ? '#fff' : '#666', display: 'flex', alignItems: 'center' }}>
          {codeA && <img src={`https://flagcdn.com/24x18/${codeA}.png`} className="flag-img" alt="flag" />}
          {match[0] ? match[0].team : 'TBD'}
        </div>
        <div style={{ padding: '5px 6px', fontSize: '0.75rem', fontWeight: 600, color: match[1] ? '#fff' : '#666', display: 'flex', alignItems: 'center' }}>
          {codeB && <img src={`https://flagcdn.com/24x18/${codeB}.png`} className="flag-img" alt="flag" />}
          {match[1] ? match[1].team : 'TBD'}
        </div>
      </div>
    );
  };

  const Column = ({ matches, title, side, nextRound }) => {
    const pairs = [];
    for (let i = 0; i < matches.length; i += 2) {
      if (i + 1 < matches.length) {
        pairs.push([matches[i], matches[i + 1]]);
      } else {
        pairs.push([matches[i]]);
      }
    }

    return (
      <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-around', margin: '0 10px', minWidth: '110px' }}>
        <div style={{ textAlign: 'center', marginBottom: '12px', color: 'var(--accent-gold)', fontWeight: 'bold', fontSize: '0.8rem', letterSpacing: '1px' }}>{title}</div>
        <div style={{ display: 'flex', flexDirection: 'column', flex: 1, justifyItems: 'stretch' }}>
          {pairs.map((pair, idx) => {
            const isAdvanced = nextRound && nextRound[idx] && nextRound[idx][0] !== null;
            const activeClass = isAdvanced ? 'active-path' : '';
            return (
              <div key={idx} className={pair.length === 2 && matches.length > 1 ? `bracket-pair-${side} ${activeClass}` : ''} style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'space-around' }}>
                <Match match={pair[0]} />
                {pair.length === 2 && <Match match={pair[1]} />}
                {pair.length === 2 && matches.length > 1 && <div className={`bracket-line-${side} ${activeClass}`}></div>}
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  const half = (arr) => [arr.slice(0, arr.length / 2), arr.slice(arr.length / 2)];
  
  const [r32L, r32R] = half(bracket.r32);
  const [r16L, r16R] = half(bracket.r16);
  const [qfL, qfR] = half(bracket.qf);
  const [sfL, sfR] = half(bracket.sf);

  return (
    <div className="scroll-reveal" style={{ marginTop: '2rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '20px' }}>
        <h2 className="heading-secondary" style={{ fontSize: '2rem' }}>TOURNAMENT BRACKET</h2>
        <button 
          onClick={startSimulation} 
          disabled={isSimulating}
          className="btn-gold"
        >
          {isSimulating ? 'Simulating...' : 'Simulate Tournament'}
        </button>
      </div>

      <div className="glass-card" style={{ 
        padding: '2rem 1rem', 
        display: 'flex', 
        justifyContent: 'center', 
        overflowX: 'auto', 
        minHeight: '600px',
        background: 'radial-gradient(circle at center, rgba(10, 15, 25, 0.6) 0%, rgba(10, 15, 25, 0.95) 100%), url(/World-Cup.png) center/cover no-repeat'
      }}>
        <div style={{ display: 'flex', width: 'max-content' }}>
          {/* Left Side */}
          <Column matches={r32L} nextRound={r16L} title="R32" side="left" />
          <Column matches={r16L} nextRound={qfL} title="R16" side="left" />
          <Column matches={qfL} nextRound={sfL} title="QF" side="left" />
          <Column matches={sfL} nextRound={[bracket.final[0]]} title="SF" side="left" />
          
          {/* Final & Winner Center */}
          <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', margin: '0 20px', minWidth: '150px' }}>
             <div style={{ textAlign: 'center', marginBottom: '16px', color: 'var(--accent-gold)', fontWeight: 'bold', fontSize: '1.2rem', letterSpacing: '1px' }}>FINAL</div>
             <Match match={bracket.final[0]} />
             
             <div style={{ marginTop: '40px', textAlign: 'center' }}>
               <div style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: '12px', fontWeight: 600 }}>WINNER</div>
               <div className={bracket.winner ? 'winner-pop' : ''} style={{ 
                 padding: '16px 24px', background: bracket.winner ? 'rgba(255,215,0,0.1)' : 'rgba(255,255,255,0.02)', 
                 border: `2px solid ${bracket.winner ? 'var(--accent-gold)' : 'var(--glass-border-light)'}`,
                 borderRadius: '12px', color: bracket.winner ? 'var(--accent-gold)' : '#666',
                 fontWeight: 'bold', fontSize: '1.6rem', fontFamily: 'var(--font-heading)',
                 boxShadow: bracket.winner ? '0 0 30px rgba(255, 215, 0, 0.2)' : 'none',
                 transition: 'all 0.5s ease',
                 display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px'
               }}>
                 {bracket.winner && <img src={`https://flagcdn.com/32x24/${getCountryCode(bracket.winner.team)}.png`} className="flag-img" style={{ width: '32px', height: '24px' }} alt="flag" />}
                 {bracket.winner ? bracket.winner.team : '???'}
               </div>
             </div>
          </div>

          {/* Right Side */}
          <Column matches={sfR} title="SF" side="right" />
          <Column matches={qfR} nextRound={sfR} title="QF" side="right" />
          <Column matches={r16R} nextRound={qfR} title="R16" side="right" />
          <Column matches={r32R} nextRound={r16R} title="R32" side="right" />
        </div>
      </div>
    </div>
  );
}
