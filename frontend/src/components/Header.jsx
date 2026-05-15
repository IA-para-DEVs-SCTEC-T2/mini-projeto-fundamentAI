import { Activity, Search, X } from 'lucide-react';
import { useState } from 'react';

export default function Header({ onSearch, currentTicker, showSearch = true }) {
  const [input, setInput] = useState(currentTicker || '');
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    const val = input.trim().toUpperCase();
    if (val) { onSearch(val); setMobileOpen(false); }
  };

  return (
    <>
      <header className="header">
        <a className="brand" onClick={() => onSearch(null)} style={{ cursor: 'pointer' }}>
          <Activity size={26} color="#00e6d2" />
          FundamentAI
        </a>

        {showSearch && (
          <>
            {/* Desktop search */}
            <div className="header-search-wrap">
              <form className="search-form" onSubmit={handleSubmit}>
                <Search className="search-icon-left" size={17} />
                <input
                  className="search-input"
                  placeholder="Buscar ticker..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  style={{ fontSize: '0.9rem', padding: '0.65rem 1rem 0.65rem 2.5rem' }}
                />
                <button type="submit" className="search-btn" style={{ padding: '0.45rem 1rem', fontSize: '0.82rem' }}>
                  Analisar
                </button>
              </form>
            </div>

            {/* Mobile search icon */}
            <button
              className="bottom-nav-btn"
              style={{ display: 'none' }}
              onClick={() => setMobileOpen(true)}
              aria-label="Buscar"
            >
              <Search size={22} />
            </button>
            <button
              onClick={() => setMobileOpen(true)}
              style={{
                display: 'none',
                background: 'none',
                border: 'none',
                color: 'var(--text-muted)',
                cursor: 'pointer',
              }}
              className="mobile-search-trigger"
              aria-label="Abrir busca"
            >
              <Search size={22} />
            </button>
          </>
        )}
      </header>

      {/* Mobile overlay */}
      {mobileOpen && (
        <div className="mobile-search-overlay">
          <form className="search-form" onSubmit={handleSubmit} style={{ maxWidth: 480, width: '100%' }}>
            <Search className="search-icon-left" size={18} />
            <input
              className="search-input"
              placeholder="Digite um Ticker (ex: PETR4, HGLG11)"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              autoFocus
            />
            <button type="submit" className="search-btn">Analisar</button>
          </form>
          <button className="btn-cancel" onClick={() => setMobileOpen(false)}>
            <X size={14} style={{ marginRight: 4 }} /> Cancelar
          </button>
        </div>
      )}
    </>
  );
}
