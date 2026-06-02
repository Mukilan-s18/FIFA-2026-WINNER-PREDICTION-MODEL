import { useTranslation } from 'react-i18next';

export default function Spotlight({ teamData }) {
  const { t } = useTranslation();
  if (!teamData) return null;
  const stars = teamData.star_player_count || 0;

  return (
    <div className="scroll-reveal" style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <h3 className="section-title" style={{ marginTop: 0 }}>{t('Team Spotlight')}</h3>
      <div className="glass-card flex" style={{ padding: 0, overflow: 'hidden', alignItems: 'stretch', flex: 1 }}>
        <div style={{
          flex: 1,
          backgroundImage: `url('/spotlight.png')`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          minHeight: '280px'
        }} />
        <div className="flex-col justify-between" style={{ flex: 1.2, padding: '1.5rem' }}>
          <div>
            <h4 className="text-gold" style={{ fontSize: '1.8rem', marginBottom: '1.2rem', fontFamily: 'var(--font-heading)' }}>{teamData.team.toUpperCase()}</h4>
            <div className="flex justify-between" style={{ marginBottom: '0.75rem' }}>
              <span className="text-muted">FIFA Rating:</span>
              <span className="text-blue text-lg" style={{ fontWeight: 600 }}>{teamData.fifa_rating || 'N/A'}</span>
            </div>
            <div className="flex justify-between" style={{ marginBottom: '0.75rem' }}>
              <span className="text-muted">Squad Value:</span>
              <span className="text-blue text-lg" style={{ fontWeight: 600 }}>€{teamData.squad_value_m || 'N/A'}M</span>
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
