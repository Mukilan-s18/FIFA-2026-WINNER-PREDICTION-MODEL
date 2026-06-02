export default function Navbar() {
  return (
    <nav className="flex items-center justify-between" style={{ padding: '24px 0', borderBottom: '1px solid var(--glass-border-light)', marginBottom: '24px' }}>
      <div className="flex items-center gap-4">
        <h2 className="text-blue" style={{ margin: 0, fontSize: '1.5rem', borderBottom: 'none', padding: 0 }}>APEX PITCH</h2>
        <span className="text-muted" style={{ fontSize: '0.9rem', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Model v4.2</span>
      </div>
      <div className="flex items-center gap-4">
        <button className="btn-primary">Simulate Now</button>
      </div>
    </nav>
  );
}
