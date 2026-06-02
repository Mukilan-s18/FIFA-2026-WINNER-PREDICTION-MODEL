export default function PowerRankings({ data }) {
  const top20 = data.slice(0, 20);
  const maxProb = Math.max(...top20.map(t => t.win_prob));

  return (
    <div>
      <h3 className="section-title" style={{ marginTop: 0 }}>Power Rankings</h3>
      <div className="glass-card flex-col gap-4" style={{ padding: '1.5rem' }}>
        {top20.map((team, idx) => {
          const width = (team.win_prob / maxProb) * 100;
          return (
            <div key={team.team} className="flex items-center gap-4" style={{ marginBottom: '8px' }}>
              <span className="text-muted" style={{ width: '20px', textAlign: 'right', fontSize: '0.9rem' }}>{idx + 1}</span>
              <span style={{ width: '120px', fontWeight: 500 }}>{team.team}</span>
              <div style={{ flex: 1, height: '8px', background: 'var(--glass-bg)', borderRadius: '4px', overflow: 'hidden' }}>
                <div style={{
                  height: '100%',
                  width: `${width}%`,
                  background: 'linear-gradient(90deg, #005f73, var(--accent-blue))',
                  borderRadius: '4px'
                }} />
              </div>
              <span className="text-blue" style={{ width: '60px', textAlign: 'right', fontFamily: 'var(--font-heading)', fontSize: '1.1rem' }}>
                {(team.win_prob * 100).toFixed(1)}%
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
