export default function TournamentProbabilities({ data }) {
  const top10 = data.slice(0, 10);

  const getFlag = (team) => {
    const flags = {
      'Brazil': '🇧🇷', 'France': '🇫🇷', 'Argentina': '🇦🇷', 'England': '🏴󠁧󠁢󠁥󠁮󠁧󠁿',
      'Spain': '🇪🇸', 'Portugal': '🇵🇹', 'Germany': '🇩🇪', 'Netherlands': '🇳🇱',
      'Italy': '🇮🇹', 'Belgium': '🇧🇪', 'Croatia': '🇭🇷', 'Uruguay': '🇺🇾'
    };
    return flags[team] || '🏳️';
  };

  return (
    <div>
      <h3 className="section-title">Tournament Progression</h3>
      <div className="glass-card" style={{ padding: '1rem 1.5rem' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th style={{ textAlign: 'left', padding: '12px 0', borderBottom: '1px solid var(--glass-border-blue)', color: 'var(--text-muted)', fontFamily: 'var(--font-heading)', letterSpacing: '0.05em' }}>TEAM</th>
              <th style={{ textAlign: 'right', padding: '12px 0', borderBottom: '1px solid var(--glass-border-blue)', color: 'var(--text-muted)', fontFamily: 'var(--font-heading)', letterSpacing: '0.05em' }}>SEMI-FINAL</th>
              <th style={{ textAlign: 'right', padding: '12px 0', borderBottom: '1px solid var(--glass-border-blue)', color: 'var(--text-muted)', fontFamily: 'var(--font-heading)', letterSpacing: '0.05em' }}>FINAL</th>
              <th style={{ textAlign: 'right', padding: '12px 0', borderBottom: '1px solid var(--glass-border-blue)', color: 'var(--accent-gold)', fontFamily: 'var(--font-heading)', letterSpacing: '0.05em' }}>WIN</th>
            </tr>
          </thead>
          <tbody>
            {top10.map((team, idx) => (
              <tr key={team.team}>
                <td style={{ padding: '16px 0', borderBottom: '1px solid var(--glass-border-light)', fontWeight: 600 }}>
                  <span style={{ marginRight: '12px', fontSize: '1.2rem' }}>{getFlag(team.team)}</span> {team.team}
                </td>
                <td style={{ textAlign: 'right', padding: '16px 0', borderBottom: '1px solid var(--glass-border-light)' }}>
                  {(team.semi_prob * 100).toFixed(1)}%
                </td>
                <td style={{ textAlign: 'right', padding: '16px 0', borderBottom: '1px solid var(--glass-border-light)' }}>
                  {(team.final_prob * 100).toFixed(1)}%
                </td>
                <td style={{ textAlign: 'right', padding: '16px 0', borderBottom: '1px solid var(--glass-border-light)', color: 'var(--accent-gold)', fontWeight: 700, fontFamily: 'var(--font-heading)', fontSize: '1.1rem' }}>
                  {(team.win_prob * 100).toFixed(1)}%
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
