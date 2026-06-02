export default function PowerRankings({ data }) {
  const top20 = data.slice(0, 20);
  const maxProb = Math.max(...top20.map(t => t.win_prob));

  return (
    <div className="scroll-reveal">
      <h3 className="section-title" style={{ marginTop: 0 }}>Power Rankings</h3>
      <div className="glass-card flex-col gap-4">
        {top20.map((team, idx) => {
          const width = (team.win_prob / maxProb) * 100;
          return (
            <div key={team.team} className="flex items-center gap-4 scroll-reveal" style={{ 
              padding: '12px', 
              borderRadius: '8px',
              background: 'rgba(255, 255, 255, 0.02)',
              transition: 'background 0.3s ease',
              marginBottom: '4px'
            }}
            onMouseOver={(e) => e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)'}
            onMouseOut={(e) => e.currentTarget.style.background = 'rgba(255, 255, 255, 0.02)'}
            >
              <span className="text-muted" style={{ width: '24px', textAlign: 'right', fontSize: '1.1rem', fontWeight: 600 }}>{idx + 1}</span>
              <div className="flex-col" style={{ width: '140px' }}>
                <span style={{ fontWeight: 600, fontSize: '1.1rem' }}>{team.team}</span>
                <span className="text-muted" style={{ fontSize: '0.8rem' }}>€{team.squad_value_m}M Value</span>
              </div>
              
              <div className="flex-col" style={{ flex: 1, gap: '4px' }}>
                <div style={{ width: '100%', height: '10px', background: 'rgba(0,0,0,0.3)', borderRadius: '5px', overflow: 'hidden' }}>
                  <div style={{
                    height: '100%',
                    width: `${width}%`,
                    background: 'linear-gradient(90deg, var(--accent-blue), #00ffcc)',
                    borderRadius: '5px',
                    boxShadow: '0 0 10px rgba(0, 229, 255, 0.5)'
                  }} />
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', justifyContent: 'space-between' }}>
                  <span>Semi: {(team.semi_prob * 100).toFixed(1)}%</span>
                  <span>Final: {(team.final_prob * 100).toFixed(1)}%</span>
                </div>
              </div>

              <span className="text-gold" style={{ width: '70px', textAlign: 'right', fontFamily: 'var(--font-heading)', fontSize: '1.4rem' }}>
                {(team.win_prob * 100).toFixed(1)}%
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
