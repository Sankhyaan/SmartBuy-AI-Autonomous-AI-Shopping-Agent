/**
 * Navbar — top application bar.
 * Shows branding, phase badge, and future navigation links.
 */
export default function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <div className="brand-logo">
          <span className="brand-icon">🛒</span>
        </div>
        <div className="brand-text">
          <span className="brand-name">ShopAgent</span>
          <span className="brand-ai">AI</span>
        </div>
      </div>

      <div className="navbar-center">
        <span className="phase-badge">Phase 2 · Browser Automation</span>
      </div>

      <div className="navbar-right">
        <div className="status-dot" title="Backend status" />
        <span className="status-label">Live</span>
      </div>
    </nav>
  );
}
