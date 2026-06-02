export default function Hero({ topTeam }) {
  const winProb = (topTeam.win_prob * 100).toFixed(1);
  const finalProb = (topTeam.final_prob * 100).toFixed(1);

  return (
    <div style={{
      position: 'relative',
      width: '100%',
      height: '450px',
      backgroundImage: `linear-gradient(rgba(17, 20, 23, 0.3), rgba(17, 20, 23, 0.9)), url('/hero.png')`,
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      borderRadius: '12px',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'flex-end',
      padding: '40px',
      border: '1px solid var(--glass-border-blue)',
      boxShadow: '0 0 30px rgba(0, 229, 255, 0.1)',
      marginBottom: '3rem'
    }}>
      <div style={{ color: 'var(--accent-gold)', letterSpacing: '2px', textTransform: 'uppercase', fontSize: '0.9rem', fontWeight: 600, marginBottom: '10px', fontFamily: 'var(--font-body)' }}>
        Live Simulation • {topTeam.team}
      </div>
      <h1 className="heading-primary" style={{ margin: 0, lineHeight: 1.1 }}>FIFA 2026 WORLD CUP</h1>
      <div style={{ fontSize: '1.5rem', color: 'var(--accent-blue)', textShadow: '0px 2px 10px rgba(0, 0, 0, 0.8)', marginTop: '5px', fontFamily: 'var(--font-heading)', textTransform: 'uppercase' }}>
        PREDICTED WINNER: <span style={{ color: 'white' }}>{topTeam.team}</span>
      </div>

      <div className="glass-card" style={{
        position: 'absolute',
        bottom: '-30px',
        right: '40px',
        display: 'flex',
        gap: '3rem',
        padding: '1.5rem 2.5rem',
        background: 'rgba(17, 20, 23, 0.75)'
      }}>
        <div className="flex-col">
          <span className="text-muted" style={{ fontSize: '0.8rem', textTransform: 'uppercase', fontWeight: 600 }}>Favorite</span>
          <span className="text-gold" style={{ fontSize: '2.5rem', fontFamily: 'var(--font-heading)', lineHeight: 1.2 }}>{topTeam.team.toUpperCase()}</span>
        </div>
        <div className="flex-col">
          <span className="text-muted" style={{ fontSize: '0.8rem', textTransform: 'uppercase', fontWeight: 600 }}>Win Probability</span>
          <span className="text-gold" style={{ fontSize: '2.5rem', fontFamily: 'var(--font-heading)', lineHeight: 1.2 }}>{winProb}%</span>
        </div>
        <div className="flex-col">
          <span className="text-muted" style={{ fontSize: '0.8rem', textTransform: 'uppercase', fontWeight: 600 }}>Reach Final</span>
          <span className="text-gold" style={{ fontSize: '2.5rem', fontFamily: 'var(--font-heading)', lineHeight: 1.2 }}>{finalProb}%</span>
        </div>
      </div>
    </div>
  );
}
