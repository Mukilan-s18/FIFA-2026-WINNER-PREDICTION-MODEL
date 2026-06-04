import { getCountryInfo, getStarPlayer } from '../utils/playerData';

export default function Hero({ topTeam }) {
  if (!topTeam) return null;
  const winProb = (topTeam.win_prob * 100).toFixed(1);
  const finalProb = (topTeam.final_prob * 100).toFixed(1);

  const goldenBoot = getStarPlayer(topTeam.team);
  const { code } = getCountryInfo(topTeam.team);
  const flagUrl = code ? `https://flagcdn.com/w320/${code}.png` : null;

  return (
    <>
      <div className="scroll-reveal" style={{
        position: 'relative',
        height: '600px',
        borderRadius: '24px',
        overflow: 'hidden',
        marginBottom: '30px',
        boxShadow: '0 20px 50px rgba(0,0,0,0.5)',
        marginTop: '20px'
      }}>
      {/* Background Image with Parallax-like positioning */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundImage: `url('/hero.png')`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundAttachment: 'fixed', /* simple parallax */
        zIndex: 1
      }} />

      {/* Dark overlay for contrast */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'linear-gradient(to right, rgba(10, 10, 15, 0.75) 0%, rgba(10, 10, 15, 0) 70%)',
        zIndex: 2
      }} />

      <div style={{
        position: 'relative',
        zIndex: 3,
        padding: '60px',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        maxWidth: '800px'
      }}>
        <h1 className="heading-primary" style={{ fontSize: '4.5rem', lineHeight: 1.1 }}>
          THE ULTIMATE <br />
          <span>WORLD CUP</span> <br />
          PREDICTION
        </h1>
        <p className="text-muted" style={{ fontSize: '1.2rem', marginTop: '1.5rem', maxWidth: '480px' }}>
          Our advanced machine learning ensemble model has analyzed over 30,000 international matches to bring you the most accurate predictions for the FIFA 2026 World Cup.
        </p>
      </div>
      </div>

      <div className="glass-card scroll-reveal" style={{
        display: 'flex',
        gap: '4rem',
        padding: '2rem 3rem',
        marginBottom: '60px',
        justifyContent: 'center',
        alignItems: 'center',
        flexWrap: 'wrap'
      }}>
        <div className="flex-col">
          <span style={{ fontSize: '0.9rem', textTransform: 'uppercase', fontWeight: 700, color: '#FFFFFF', letterSpacing: '1px', textShadow: '0 2px 4px rgba(0,0,0,0.8)' }}>Favorite</span>
          <span className="text-gold" style={{ fontSize: '2.5rem', fontFamily: 'var(--font-heading)', lineHeight: 1.2, display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            {flagUrl && <img src={flagUrl} alt="" style={{ width: '45px', height: '30px', objectFit: 'cover', borderRadius: '4px', boxShadow: '0 2px 4px rgba(0,0,0,0.5)' }} />}
            {topTeam.team.toUpperCase()}
          </span>
        </div>
        <div className="flex-col">
          <span style={{ fontSize: '0.9rem', textTransform: 'uppercase', fontWeight: 700, color: '#FFFFFF', letterSpacing: '1px', textShadow: '0 2px 4px rgba(0,0,0,0.8)' }}>Win Probability</span>
          <span style={{ color: '#fff', fontSize: '2.5rem', fontFamily: 'var(--font-heading)', lineHeight: 1.2, textShadow: '0 0 10px rgba(212, 175, 55, 0.3)' }}>{winProb}%</span>
        </div>
        <div className="flex-col">
          <span style={{ fontSize: '0.9rem', textTransform: 'uppercase', fontWeight: 700, color: '#FFFFFF', letterSpacing: '1px', textShadow: '0 2px 4px rgba(0,0,0,0.8)' }}>Reach Final</span>
          <span style={{ fontSize: '2.5rem', fontFamily: 'var(--font-heading)', lineHeight: 1.2 }}>{finalProb}%</span>
        </div>
        <div style={{ display: 'flex', flexDirection: 'row', alignItems: 'center', gap: '15px' }}>
          <div className="flex-col">
            <span style={{ fontSize: '0.9rem', textTransform: 'uppercase', fontWeight: 700, color: '#FFFFFF', letterSpacing: '1px', textShadow: '0 2px 4px rgba(0,0,0,0.8)' }}>Golden Boot</span>
            <span className="text-gold" style={{ fontSize: '2.5rem', fontFamily: 'var(--font-heading)', lineHeight: 1.2, textShadow: '0 0 10px rgba(255, 215, 0, 0.3)', whiteSpace: 'nowrap', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              {flagUrl && <img src={flagUrl} alt="" style={{ width: '45px', height: '30px', objectFit: 'cover', borderRadius: '4px', boxShadow: '0 2px 4px rgba(0,0,0,0.5)' }} />}
              {goldenBoot}
            </span>
          </div>
          {['brazil', 'germany', 'argentina', 'colombia', 'portugal', 'spain', 'france', 'england', 'netherlands', 'croatia'].includes(topTeam.team.toLowerCase()) && (
            <img 
              src={`/${topTeam.team.toLowerCase()}_custom_cutout.png`} 
              onError={(e) => { 
                if (!e.target.dataset.fallback) {
                  e.target.dataset.fallback = true;
                  e.target.src = `/${topTeam.team.toLowerCase()}_cutout.png`;
                } else {
                  e.target.style.display = 'none';
                }
              }}
              alt="Player Cutout" 
              style={{ 
                height: '110px', 
                width: 'auto',
                objectFit: 'contain',
                objectPosition: 'bottom center',
                filter: 'drop-shadow(0px 4px 6px rgba(0,0,0,0.5))',
                margin: '-20px 0'
              }} 
            />
          )}
        </div>
      </div>
    </>
  );
}
