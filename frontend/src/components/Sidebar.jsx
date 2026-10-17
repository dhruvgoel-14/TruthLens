const items = [
  { id: "analyze", label: "Analyze claim", icon: "M11 4a7 7 0 1 0 0 14 7 7 0 0 0 0-14zm9 16-3.5-3.5" },
  {
    id: "community",
    label: "Community Fact-Checks",
    icon: "M9 5a3 3 0 1 0 0 6 3 3 0 0 0 0-6zM3 20c0-3.3 2.7-6 6-6s6 2.7 6 6M16 5a3 3 0 0 1 0 6M21 20c0-2.6-1.6-4.8-4-5.6",
  },
];

export default function Sidebar({ view, onChange }) {
  return (
    <aside className="sidebar">
      <a className="brand" href="#home" onClick={() => onChange("analyze")}>
        {/* Replace frontend/public/logo.svg with your own logo (same file name). */}
        <img src="/logo.svg" alt="" className="brand-logo" />
        <span>
          <strong>TruthLens</strong>
          <small>AI-powered fact checking</small>
        </span>
      </a>

      <div className="sidebar-label">WORKSPACE</div>
      <nav className="side-nav" aria-label="Main navigation">
        {items.map((item) => (
          <button
            key={item.id}
            className={view === item.id ? "nav-item active" : "nav-item"}
            onClick={() => onChange(item.id)}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
              <path d={item.icon} />
            </svg>
            {item.label}
          </button>
        ))}
      </nav>

      <div className="status-card">
        <i />
        <div>
          <strong>Live analysis</strong>
          <small>Connected to backend API</small>
        </div>
      </div>
    </aside>
  );
}
