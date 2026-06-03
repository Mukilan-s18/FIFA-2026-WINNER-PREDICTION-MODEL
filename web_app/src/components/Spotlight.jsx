import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { getCountryInfo } from './PowerRankings';

export default function Spotlight({ teams }) {
  const { t } = useTranslation();
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    if (!teams || teams.length === 0) return;
    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % teams.length);
    }, 3500);
    return () => clearInterval(interval);
  }, [teams]);

  if (!teams || teams.length === 0) return null;
  const teamData = teams[currentIndex];
  const stars = teamData.star_player_count || 0;
  
  const { code } = getCountryInfo(teamData.team);
  const flagUrl = code ? `https://flagcdn.com/w320/${code}.png` : null;

  // Map to check if we generated a custom cinematic image for this team
  const customImages = ['brazil', 'germany', 'argentina', 'colombia', 'portugal'];
  const teamNameLower = teamData.team.toLowerCase();
  
  // If we have a custom image, use it. Otherwise, fallback to the generic spotlight
  const spotlightImage = customImages.includes(teamNameLower) 
    ? `/${teamNameLower}_spotlight.png` 
    : '/spotlight.png';

  return (
    <div className="scroll-reveal" style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <h3 className="section-title" style={{ marginTop: 0 }}>{t('Team Spotlight')}</h3>
      <div className="glass-card flex" style={{ padding: 0, overflow: 'hidden', alignItems: 'stretch', flex: 1, position: 'relative' }}>
        
        {/* Left Side: Cinematic Player Image */}
        <div style={{
          flex: 1,
          backgroundImage: `url('${spotlightImage}')`,
          backgroundSize: 'cover',
          backgroundPosition: 'top center',
          minHeight: '280px',
          borderRight: '1px solid var(--glass-border-light)',
          transition: 'background-image 0.5s ease-in-out'
        }} />

        {/* Right Side: Stats and Flag */}
        <div 
          key={currentIndex} 
          className="flex-col justify-between" 
          style={{ 
            flex: 1.2, 
            padding: '1.5rem',
            animation: 'fadeInSlide 0.5s ease-out forwards'
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
              <span className="text-muted">Star Players:</span>
              <span className="text-gold">{stars > 0 ? '⭐'.repeat(stars) : 'None'}</span>
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
      </div>
    </div>
  );
}
