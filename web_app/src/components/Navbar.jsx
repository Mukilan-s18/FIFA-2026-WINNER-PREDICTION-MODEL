export default function Navbar() {
  return (
    <nav style={{ 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'center', 
      gap: '20px', 
      padding: '24px 0', 
      borderBottom: '1px solid var(--glass-border-light)', 
      marginBottom: '24px',
      width: '100%'
    }}>
      <img src="/trophy.png?v=2" alt="World Cup Trophy" style={{ height: '60px', objectFit: 'contain', mixBlendMode: 'screen', filter: 'brightness(1.1)' }} />
      <h2 style={{ margin: 0, fontSize: '2.2rem', borderBottom: 'none', padding: 0, color: 'var(--accent-gold)', letterSpacing: '0.05em', fontWeight: 'bold' }}>
        FIFA WC 2026 Predictor
      </h2>
    </nav>
  );
}
