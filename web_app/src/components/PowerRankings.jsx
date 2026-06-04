import { getCountryInfo } from '../utils/playerData';

export default function PowerRankings({ data }) {
  const top20 = data.slice(0, 20);
  const maxProb = Math.max(...top20.map(t => t.win_prob));

  return (
    <div className="scroll-reveal">
      <h3 className="section-title" style={{ marginTop: 0 }}>Power Rankings</h3>
      <div className="glass-card flex gap-4" style={{ 
        overflowX: 'auto', 
        paddingBottom: '20px',
        scrollbarWidth: 'thin',
        scrollbarColor: 'var(--accent-gold) rgba(0,0,0,0.2)'
      }}>
        {top20.map((team, idx) => {
          const width = (team.win_prob / maxProb) * 100;
          const { code, playerId } = getCountryInfo(team.team);
          const playerUrl = playerId ? `https://cdn.sofifa.net/players/${playerId.toString().padStart(6, '0').slice(0,3)}/${playerId.toString().padStart(6, '0').slice(3,6)}/24_120.png` : null;
          
          return (
            <div key={team.team} className="flex-col scroll-reveal" style={{ 
              minWidth: '280px',
              padding: '20px', 
              borderRadius: '12px',
              background: code ? `linear-gradient(to right, rgba(10, 15, 25, 0.75) 30%, rgba(10, 15, 25, 0.1) 100%), url(https://flagcdn.com/w320/${code}.png) center/cover` : 'rgba(255, 255, 255, 0.02)',
              border: '1px solid var(--glass-border-light)',
              transition: 'transform 0.3s ease, box-shadow 0.3s ease, background-image 0.3s ease',
              cursor: 'default',
              position: 'relative'
            }}
            onMouseOver={(e) => { 
              if (code) {
                e.currentTarget.style.backgroundImage = `linear-gradient(to right, rgba(10, 15, 25, 0.65) 20%, rgba(10, 15, 25, 0) 100%), url(https://flagcdn.com/w320/${code}.png)`;
              } else {
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.06)'; 
              }
              e.currentTarget.style.transform = 'translateY(-6px)';
              e.currentTarget.style.boxShadow = '0 10px 20px rgba(0,0,0,0.3)';
            }}
            onMouseOut={(e) => { 
              if (code) {
                e.currentTarget.style.backgroundImage = `linear-gradient(to right, rgba(10, 15, 25, 0.75) 30%, rgba(10, 15, 25, 0.1) 100%), url(https://flagcdn.com/w320/${code}.png)`;
              } else {
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.02)'; 
              }
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = 'none';
            }}
            >
              {playerUrl && (
                <div style={{
                  position: 'absolute',
                  bottom: '0',
                  right: '0',
                  width: '130px',
                  height: '100%',
                  zIndex: 1,
                  overflow: 'hidden',
                  borderBottomRightRadius: '12px'
                }}>
                  <img 
                    src={playerUrl} 
                    alt="captain" 
                    referrerPolicy="no-referrer"
                    style={{
                      position: 'absolute',
                      bottom: '5px',
                      right: '-15px',
                      height: '170px',
                      opacity: 1,
                      filter: 'drop-shadow(-5px 0px 8px rgba(0,0,0,0.8)) brightness(1.15) contrast(1.05)'
                    }}
                  />
                  <div style={{
                    position: 'absolute',
                    bottom: 0, left: 0, right: 0, height: '40px',
                    background: 'linear-gradient(to top, rgba(10,15,25,0.7), transparent)'
                  }} />
                </div>
              )}
              <div className="flex items-end" style={{ marginBottom: '12px', position: 'relative', zIndex: 2, gap: '12px' }}>
                <span className="text-muted" style={{ fontSize: '1.2rem', fontWeight: 700 }}>#{idx + 1}</span>
                <span className="text-gold" style={{ fontFamily: 'var(--font-heading)', fontSize: '1.8rem', lineHeight: 0.9 }}>
                  {(team.win_prob * 100).toFixed(1)}%
                </span>
              </div>
              
              <div className="flex-col" style={{ marginBottom: '20px', position: 'relative', zIndex: 2, maxWidth: '150px' }}>
                <span style={{ fontWeight: 600, fontSize: '1.4rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', display: 'flex', alignItems: 'center', textShadow: '0 2px 4px rgba(0,0,0,0.8)' }}>
                  {code && <img src={`https://flagcdn.com/24x18/${code}.png`} alt="flag" style={{ width: '24px', borderRadius: '3px', marginRight: '8px', boxShadow: '0 0 5px rgba(0,0,0,0.5)' }} />}
                  {team.team}
                </span>
                <span className="text-muted" style={{ fontSize: '0.8rem', opacity: 0.8, textShadow: '0 1px 2px rgba(0,0,0,0.8)' }}>€{team.squad_value_m}M Value</span>
              </div>
              
              <div className="flex-col" style={{ gap: '8px', marginTop: 'auto', position: 'relative', zIndex: 2, paddingRight: '110px' }}>
                <div style={{ width: '100%', height: '8px', background: 'rgba(0,0,0,0.4)', borderRadius: '4px', overflow: 'hidden', boxShadow: 'inset 0 1px 3px rgba(0,0,0,0.5)' }}>
                  <div style={{
                    height: '100%',
                    width: `${width}%`,
                    background: 'linear-gradient(90deg, #D4AF37, #FFDF73)',
                    borderRadius: '4px',
                    boxShadow: '0 0 10px rgba(212, 175, 55, 0.5)'
                  }} />
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', gap: '12px' }}>
                  <span>Semi: {(team.semi_prob * 100).toFixed(1)}%</span>
                  <span>Final: {(team.final_prob * 100).toFixed(1)}%</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
