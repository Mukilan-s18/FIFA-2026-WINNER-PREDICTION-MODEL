import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { getCountryInfo, getStarPlayer } from '../utils/playerData';

export default function Spotlight({ teams }) {
  const { t } = useTranslation();
  const [currentIndex, setCurrentIndex] = useState(0);
  const [cacheVersion] = useState(() => Date.now());

  useEffect(() => {
    if (!teams || teams.length === 0) return;
    
    // Preload cinematic images to prevent lag during the slider cycle
    const customImages = ['brazil', 'germany', 'argentina', 'colombia', 'portugal', 'spain', 'france', 'england', 'netherlands', 'croatia'];
    teams.forEach(t => {
      const teamNameLower = t.team.toLowerCase();
      if (customImages.includes(teamNameLower)) {
        const img = new Image();
        img.src = `/${teamNameLower}_spotlight.png?v=${cacheVersion}`;
      }
    });

    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % teams.length);
    }, 7000);
    return () => clearInterval(interval);
  }, [teams, cacheVersion]);

  if (!teams || teams.length === 0) return null;
  
  // Map to check if we generated a custom cinematic image for this team
  const customImages = ['brazil', 'germany', 'argentina', 'colombia', 'portugal', 'spain', 'france', 'england', 'netherlands', 'croatia'];

  return (
    <div className="scroll-reveal" style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <h3 className="section-title" style={{ marginTop: 0 }}>{t('Team Spotlight')}</h3>
      <div className="glass-card flex responsive-flex" style={{ padding: 0, overflow: 'hidden', alignItems: 'stretch', flex: 1, position: 'relative' }}>
        
        {/* Left Side: Cinematic Player Images (Crossfading) */}
        <div className="spotlight-left responsive-border-right" style={{ flex: 1, position: 'relative', minHeight: '280px', borderRight: '1px solid var(--glass-border-light)' }}>
          {teams.map((teamData, index) => {
            const teamNameLower = teamData.team.toLowerCase();
            const spotlightImage = customImages.includes(teamNameLower) 
              ? `/${teamNameLower}_spotlight.png?v=${cacheVersion}` 
              : '/spotlight.png';
            return (
              <div
                key={`img-${teamData.team}`}
                style={{
                  position: 'absolute', top: 0, left: 0, right: 0, bottom: 0,
                  backgroundImage: `url('${spotlightImage}')`,
                  backgroundSize: 'cover', backgroundPosition: 'top center',
                  opacity: index === currentIndex ? 1 : 0,
                  transition: 'opacity 1.5s ease-in-out',
                  zIndex: index === currentIndex ? 1 : 0
                }}
              />
            );
          })}
        </div>

        {/* Right Side: Stats and Flag (Crossfading) */}
        <div style={{ flex: 1.2, position: 'relative' }}>
          {teams.map((teamData, index) => {
            const { code } = getCountryInfo(teamData.team);
            const flagUrl = code ? `https://flagcdn.com/w320/${code}.png` : null;
            return (
              <div 
                key={`stats-${teamData.team}`}
                className="flex-col justify-between" 
                style={{ 
                  position: index === 0 ? 'relative' : 'absolute', 
                  top: 0, left: 0, right: 0, bottom: 0,
                  height: '100%',
                  padding: '1.5rem',
                  opacity: index === currentIndex ? 1 : 0,
                  visibility: index === currentIndex ? 'visible' : 'hidden',
                  transition: 'opacity 1s ease-in-out, visibility 1s',
                  pointerEvents: index === currentIndex ? 'auto' : 'none',
                  zIndex: index === currentIndex ? 1 : 0
                }}
              >
                <div>
                  <div className="flex items-center gap-3" style={{ marginBottom: '1.2rem' }}>
                    {flagUrl && <img src={flagUrl} alt="Flag" style={{ width: '36px', height: '24px', objectFit: 'cover', borderRadius: '4px', boxShadow: '0 2px 5px rgba(0,0,0,0.3)' }} />}
                    <h4 className="text-gold" style={{ fontSize: '1.8rem', margin: 0, fontFamily: 'var(--font-heading)', lineHeight: 1 }}>{teamData.team.toUpperCase()}</h4>
                  </div>
                  <div className="flex justify-between" style={{ marginBottom: '0.75rem' }}>
                    <span className="text-muted">FIFA Rating:</span>
                    <span className="text-gold text-lg" style={{ fontWeight: 600 }}>{teamData.fifa_rating || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between" style={{ marginBottom: '0.75rem' }}>
                    <span className="text-muted">Squad Value:</span>
                    <span className="text-gold text-lg" style={{ fontWeight: 600 }}>€{teamData.squad_value_m || 'N/A'}M</span>
                  </div>
                  <div className="flex justify-between" style={{ marginBottom: '0.75rem' }}>
                    <span className="text-muted">Continent:</span>
                    <span style={{ fontWeight: 500 }}>{teamData.home_continent || 'Unknown'}</span>
                  </div>
                  <div className="flex justify-between" style={{ marginBottom: '0.75rem' }}>
                    <span className="text-muted">Star Player:</span>
                    <span className="text-gold flex items-center gap-2">
                      {flagUrl && <img src={flagUrl} alt="" style={{ width: '20px', height: '14px', borderRadius: '2px' }} />}
                      {getStarPlayer(teamData.team)}
                    </span>
                  </div>
                </div>
                <div style={{ marginTop: '1.5rem', borderTop: '1px solid var(--glass-border-light)', paddingTop: '1.5rem' }}>
                  <div className="flex justify-between items-center">
                    <span className="text-muted text-sm" style={{ textTransform: 'uppercase', fontWeight: 600 }}>Win Prob</span>
                    <span className="text-gold" style={{ fontSize: '2rem', fontFamily: 'var(--font-heading)', lineHeight: 1 }}>
                      {(teamData.win_prob * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
