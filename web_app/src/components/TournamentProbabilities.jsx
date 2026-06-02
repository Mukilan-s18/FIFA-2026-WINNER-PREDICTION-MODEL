import { useTranslation } from 'react-i18next';

export default function TournamentProbabilities({ data }) {
  const { t } = useTranslation();
  const top10 = data.slice(0, 10);

  const getCountryCode = (teamName) => {
    const map = {
      'Brazil': 'br', 'France': 'fr', 'Argentina': 'ar', 'England': 'gb-eng',
      'Spain': 'es', 'Portugal': 'pt', 'Germany': 'de', 'Netherlands': 'nl',
      'Italy': 'it', 'Belgium': 'be', 'Croatia': 'hr', 'Uruguay': 'uy',
      'Colombia': 'co', 'USA': 'us', 'Mexico': 'mx', 'Switzerland': 'ch',
      'Senegal': 'sn', 'Japan': 'jp', 'Morocco': 'ma', 'South Korea': 'kr',
      'Denmark': 'dk', 'Ecuador': 'ec', 'Turkey': 'tr', 'Serbia': 'rs',
      'Nigeria': 'ng', 'Iran': 'ir', 'Canada': 'ca', 'Peru': 'pe',
      'Paraguay': 'py'
    };
    return map[teamName] || null;
  };

  return (
    <div className="scroll-reveal" style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <h3 className="section-title" style={{ marginTop: 0 }}>Tournament Progression</h3>
      <div className="glass-card" style={{ padding: '1rem 1.5rem', flex: 1 }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th style={{ textAlign: 'left', padding: '12px 0', borderBottom: '1px solid var(--glass-border-blue)', color: 'var(--text-muted)', fontFamily: 'var(--font-heading)', letterSpacing: '0.05em' }}>{t('TEAM')}</th>
              <th style={{ textAlign: 'right', padding: '12px 0', borderBottom: '1px solid var(--glass-border-blue)', color: 'var(--text-muted)', fontFamily: 'var(--font-heading)', letterSpacing: '0.05em' }}>SEMI-FINAL</th>
              <th style={{ textAlign: 'right', padding: '12px 0', borderBottom: '1px solid var(--glass-border-blue)', color: 'var(--text-muted)', fontFamily: 'var(--font-heading)', letterSpacing: '0.05em' }}>FINAL</th>
              <th style={{ textAlign: 'right', padding: '12px 0', borderBottom: '1px solid var(--glass-border-blue)', color: 'var(--accent-gold)', fontFamily: 'var(--font-heading)', letterSpacing: '0.05em' }}>WIN</th>
            </tr>
          </thead>
          <tbody>
            {top10.map((team, idx) => (
              <tr key={team.team}>
                <td style={{ padding: '16px 0', borderBottom: '1px solid var(--glass-border-light)', fontWeight: 600 }}>
                  <div style={{ display: 'flex', alignItems: 'center' }}>
                    {getCountryCode(team.team) ? (
                      <img src={`https://flagcdn.com/24x18/${getCountryCode(team.team)}.png`} alt="flag" style={{ width: '24px', borderRadius: '3px', marginRight: '12px', boxShadow: '0 0 5px rgba(0,0,0,0.5)' }} />
                    ) : (
                      <span style={{ marginRight: '12px', fontSize: '1.2rem' }}>🏳️</span>
                    )}
                    {team.team}
                  </div>
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
