export default function Hero({ topTeam }) {
  if (!topTeam) return null;
  const winProb = (topTeam.win_prob * 100).toFixed(1);
  const finalProb = (topTeam.final_prob * 100).toFixed(1);

  // Heuristic: The Golden Boot winner usually comes from the team that makes it the furthest (most matches played).
  // We predict the star forward of the highest probability team to win the Golden Boot.
  const getStarPlayer = (team) => {
    const stars = {
      'Spain': 'Lamine Yamal',
      'Argentina': 'Lionel Messi',
      'France': 'Kylian Mbappé',
      'England': 'Harry Kane',
      'Brazil': 'Vinícius Júnior',
      'Portugal': 'Cristiano Ronaldo',
      'Netherlands': 'Cody Gakpo',
      'Germany': 'Jamal Musiala',
      'Colombia': 'Luis Díaz',
      'Croatia': 'Luka Modrić'
    };
    return stars[team] || 'Top Goalscorer';
  };

  const goldenBoot = getStarPlayer(topTeam.team);

  return (
    <div className="scroll-reveal" style={{
      position: 'relative',
      height: '600px',
      borderRadius: '24px',
      overflow: 'hidden',
      marginBottom: '60px',
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

      <div className="glass-card scroll-reveal" style={{
        position: 'absolute',
        bottom: '15px',
        right: '15px',
        display: 'flex',
        gap: '2rem',
        padding: '1.5rem 2rem',
        zIndex: 3
      }}>
        <div className="flex-col">
          <span style={{ fontSize: '0.9rem', textTransform: 'uppercase', fontWeight: 700, color: '#FFFFFF', letterSpacing: '1px', textShadow: '0 2px 4px rgba(0,0,0,0.8)' }}>Favorite</span>
          <span className="text-gold" style={{ fontSize: '2.5rem', fontFamily: 'var(--font-heading)', lineHeight: 1.2 }}>{topTeam.team.toUpperCase()}</span>
        </div>
        <div className="flex-col">
          <span style={{ fontSize: '0.9rem', textTransform: 'uppercase', fontWeight: 700, color: '#FFFFFF', letterSpacing: '1px', textShadow: '0 2px 4px rgba(0,0,0,0.8)' }}>Win Probability</span>
          <span style={{ color: '#fff', fontSize: '2.5rem', fontFamily: 'var(--font-heading)', lineHeight: 1.2, textShadow: '0 0 10px rgba(212, 175, 55, 0.3)' }}>{winProb}%</span>
        </div>
        <div className="flex-col">
          <span style={{ fontSize: '0.9rem', textTransform: 'uppercase', fontWeight: 700, color: '#FFFFFF', letterSpacing: '1px', textShadow: '0 2px 4px rgba(0,0,0,0.8)' }}>Reach Final</span>
          <span style={{ fontSize: '2.5rem', fontFamily: 'var(--font-heading)', lineHeight: 1.2 }}>{finalProb}%</span>
        </div>
        <div className="flex-col">
          <span style={{ fontSize: '0.9rem', textTransform: 'uppercase', fontWeight: 700, color: '#FFFFFF', letterSpacing: '1px', textShadow: '0 2px 4px rgba(0,0,0,0.8)' }}>Golden Boot</span>
          <span className="text-gold" style={{ fontSize: '1.8rem', fontFamily: 'var(--font-heading)', lineHeight: 1.2, textShadow: '0 0 10px rgba(255, 215, 0, 0.3)', whiteSpace: 'nowrap' }}>{goldenBoot}</span>
        </div>
      </div>
    </div>
  );
}
