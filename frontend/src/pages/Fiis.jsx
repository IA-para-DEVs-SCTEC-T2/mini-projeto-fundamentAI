import { useState, useMemo } from 'react';
import { Building2, Search, ArrowUpDown, X } from 'lucide-react';
import ScoreRing, { scoreLabel } from '../components/ScoreRing';

// ── Mock data (Etapa 4 substitui por API) ────────────────────────────────────
const MOCK_FIIS = [
  { ticker: 'HGLG11', name: 'CSHG Logística',         segment: 'Logística',       price: 162.50, change: +0.31, score: 81, dy: '9,8%',  pvp: 0.95 },
  { ticker: 'XPML11', name: 'XP Malls',               segment: 'Shopping',        price:  98.40, change: +0.55, score: 76, dy: '8,9%',  pvp: 0.98 },
  { ticker: 'MXRF11', name: 'Maxi Renda',             segment: 'Papel',           price:  10.42, change: +0.19, score: 70, dy: '12,1%', pvp: 1.02 },
  { ticker: 'KNRI11', name: 'Kinea Renda Imobiliária', segment: 'Híbrido',        price: 148.20, change: -0.20, score: 78, dy: '7,5%',  pvp: 0.92 },
  { ticker: 'VISC11', name: 'Vinci Shopping Centers', segment: 'Shopping',        price:  96.80, change: +0.40, score: 74, dy: '8,2%',  pvp: 0.97 },
  { ticker: 'BCFF11', name: 'BTG Pactual Fundo de Fundos', segment: 'Fundo de Fundos', price: 72.30, change: -0.10, score: 65, dy: '9,3%', pvp: 0.88 },
  { ticker: 'HFOF11', name: 'Hedge Top FOFII',        segment: 'Fundo de Fundos', price:  74.50, change: +0.25, score: 67, dy: '9,1%',  pvp: 0.90 },
  { ticker: 'GGRC11', name: 'GGR Covepi Renda',       segment: 'Logística',       price: 108.60, change: +0.60, score: 79, dy: '10,2%', pvp: 0.93 },
  { ticker: 'BRCO11', name: 'Bresco Logística',       segment: 'Logística',       price: 102.40, change: +0.15, score: 77, dy: '8,7%',  pvp: 0.96 },
  { ticker: 'RBRP11', name: 'RBR Properties',         segment: 'Escritórios',     price:  68.90, change: -0.35, score: 62, dy: '8,0%',  pvp: 0.85 },
  { ticker: 'BRCR11', name: 'BC Fund',                segment: 'Escritórios',     price:  68.10, change: -0.50, score: 58, dy: '7,8%',  pvp: 0.82 },
  { ticker: 'PVBI11', name: 'VBI Prime Properties',   segment: 'Escritórios',     price:  88.20, change: +0.30, score: 71, dy: '8,4%',  pvp: 0.94 },
  { ticker: 'TRXF11', name: 'TRX Real Estate',        segment: 'Renda Urbana',    price:  96.50, change: +0.45, score: 75, dy: '9,5%',  pvp: 0.99 },
  { ticker: 'ALZR11', name: 'Alianza Trust Renda',    segment: 'Renda Urbana',    price: 112.30, change: +0.20, score: 73, dy: '8,6%',  pvp: 0.97 },
  { ticker: 'CPTS11', name: 'Capitânia Securities II', segment: 'Papel',          price:  88.70, change: -0.15, score: 68, dy: '11,5%', pvp: 0.91 },
  { ticker: 'KNCR11', name: 'Kinea Rendimentos',      segment: 'Papel',           price: 102.80, change: +0.10, score: 72, dy: '10,8%', pvp: 1.00 },
  { ticker: 'RBRF11', name: 'RBR Alpha Fundo de Fundos', segment: 'Fundo de Fundos', price: 72.10, change: +0.05, score: 64, dy: '9,0%', pvp: 0.87 },
  { ticker: 'HSML11', name: 'HSI Malls',              segment: 'Shopping',        price:  82.60, change: +0.35, score: 69, dy: '8,3%',  pvp: 0.93 },
  { ticker: 'MALL11', name: 'Malls Brasil Plural',    segment: 'Shopping',        price:  88.40, change: +0.50, score: 71, dy: '8,1%',  pvp: 0.95 },
  { ticker: 'HGBS11', name: 'Hedge Brasil Shopping',  segment: 'Shopping',        price: 196.80, change: -0.25, score: 66, dy: '7,9%',  pvp: 0.89 },
  { ticker: 'VRTA11', name: 'Fator Verita',           segment: 'Papel',           price:  96.20, change: +0.20, score: 70, dy: '11,2%', pvp: 0.98 },
  { ticker: 'HGCR11', name: 'CSHG Recebíveis',        segment: 'Papel',           price:  98.50, change: +0.15, score: 69, dy: '10,9%', pvp: 0.99 },
  { ticker: 'XPLG11', name: 'XP Log',                 segment: 'Logística',       price: 102.10, change: +0.40, score: 76, dy: '9,2%',  pvp: 0.94 },
  { ticker: 'LVBI11', name: 'VBI Logístico',          segment: 'Logística',       price: 108.30, change: +0.25, score: 74, dy: '9,0%',  pvp: 0.96 },
  { ticker: 'BTLG11', name: 'BTG Pactual Logística',  segment: 'Logística',       price: 102.60, change: +0.35, score: 75, dy: '9,1%',  pvp: 0.95 },
];

// ── Opções de ordenação ───────────────────────────────────────────────────────
const SORT_OPTIONS = [
  { value: 'score_desc',  label: '↓ Maior Score' },
  { value: 'score_asc',   label: '↑ Menor Score' },
  { value: 'dy_desc',     label: '↓ Maior DY' },
  { value: 'pvp_asc',     label: '↑ Menor P/VP' },
  { value: 'change_desc', label: '↓ Maior Variação' },
  { value: 'change_asc',  label: '↑ Menor Variação' },
  { value: 'price_desc',  label: '↓ Maior Preço' },
  { value: 'price_asc',   label: '↑ Menor Preço' },
  { value: 'az',          label: 'A → Z (Ticker)' },
];

// ── Helpers ───────────────────────────────────────────────────────────────────
function scoreColor(score) {
  if (score >= 75) return '#00C853';
  if (score >= 50) return '#FFD600';
  return '#FF5252';
}

function parseDy(dy) {
  return parseFloat(dy.replace(',', '.').replace('%', ''));
}

// ── Main component ─────────────────────────────────────────────────────────────
export default function Fiis({ onSearch }) {
  const [query, setQuery]   = useState('');
  const [segment, setSegment] = useState('Todos');
  const [sortBy, setSortBy] = useState('score_desc');

  const segments = useMemo(() => {
    const s = [...new Set(MOCK_FIIS.map((f) => f.segment))].sort();
    return ['Todos', ...s];
  }, []);

  const filtered = useMemo(() => {
    let list = [...MOCK_FIIS];
    if (query.trim()) {
      const q = query.trim().toUpperCase();
      list = list.filter(
        (f) => f.ticker.includes(q) || f.name.toUpperCase().includes(q)
      );
    }
    if (segment !== 'Todos') {
      list = list.filter((f) => f.segment === segment);
    }
    list.sort((a, b) => {
      switch (sortBy) {
        case 'score_desc':  return b.score  - a.score;
        case 'score_asc':   return a.score  - b.score;
        case 'dy_desc':     return parseDy(b.dy) - parseDy(a.dy);
        case 'pvp_asc':     return a.pvp - b.pvp;
        case 'change_desc': return b.change - a.change;
        case 'change_asc':  return a.change - b.change;
        case 'price_desc':  return b.price  - a.price;
        case 'price_asc':   return a.price  - b.price;
        case 'az':          return a.ticker.localeCompare(b.ticker);
        default:            return 0;
      }
    });
    return list;
  }, [query, segment, sortBy]);

  const hasActiveFilters = segment !== 'Todos' || sortBy !== 'score_desc' || query.trim();

  const clearFilters = () => {
    setSegment('Todos');
    setSortBy('score_desc');
    setQuery('');
  };

  return (
    <div className="acoes-page fiis-page">

      {/* Header */}
      <div className="acoes-header">
        <div className="acoes-header-left">
          <Building2 size={22} color="#8a2be2" />
          <div>
            <h1 className="acoes-title" style={{ background: 'linear-gradient(135deg, #fff 30%, #8a2be2)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              FIIs
            </h1>
            <p className="acoes-sub">Fundos de Investimento Imobiliário listados na B3</p>
          </div>
        </div>
        <div className="acoes-search-wrap">
          <div className="acoes-search-inner">
            <Search size={15} color="var(--text-muted)" style={{ flexShrink: 0 }} />
            <input
              className="acoes-search-input"
              placeholder="Buscar ticker ou fundo..."
              value={query}
              onChange={(e) => setQuery(e.target.value.toUpperCase())}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && query.trim()) onSearch(query.trim());
              }}
            />
            {query && (
              <button className="acoes-search-clear" onClick={() => setQuery('')} aria-label="Limpar">
                <X size={13} />
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Filtros por segmento */}
      <div className="acoes-filter-bar">
        <div className="acoes-sector-chips">
          {segments.map((s) => (
            <button
              key={s}
              className={`acoes-sector-chip fii-chip${segment === s ? ' fii-chip-active' : ''}`}
              onClick={() => setSegment(s)}
            >
              {s}
            </button>
          ))}
        </div>
        <div className="acoes-sort-row">
          <div className="acoes-sort-wrap">
            <ArrowUpDown size={13} color="var(--text-muted)" />
            <select
              className="acoes-sort-select"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
            >
              {SORT_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>{o.label}</option>
              ))}
            </select>
          </div>
          {hasActiveFilters && (
            <button className="acoes-clear-btn" onClick={clearFilters}>
              <X size={12} /> Limpar
            </button>
          )}
        </div>
      </div>

      {/* Contador */}
      <div className="acoes-count">
        <span className="acoes-count-num" style={{ color: '#8a2be2' }}>{filtered.length}</span>
        <span className="acoes-count-label">
          {filtered.length === 1 ? 'FII encontrado' : 'FIIs encontrados'}
          {segment !== 'Todos' && ` em ${segment}`}
        </span>
      </div>

      {/* Grid ou empty state */}
      {filtered.length === 0 ? (
        <div className="acoes-empty">
          <div className="acoes-empty-icon">🏢</div>
          <div className="acoes-empty-text">Nenhum FII encontrado</div>
          <button className="acoes-clear-btn" onClick={clearFilters}>Limpar filtros</button>
        </div>
      ) : (
        <div className="acoes-grid">
          {filtered.map((f) => {
            const isUp  = f.change >= 0;
            const color = scoreColor(f.score);
            const label = scoreLabel(f.score);
            return (
              <button key={f.ticker} className="acoes-card fii-card" onClick={() => onSearch(f.ticker)}>
                <div className="acoes-card-top">
                  <div style={{ minWidth: 0, flex: 1 }}>
                    <div className="acoes-card-ticker">{f.ticker}</div>
                    <div className="acoes-card-name" style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '100%' }}>{f.name}</div>
                    <div className="acoes-card-sector fii-segment-tag">{f.segment}</div>
                  </div>
                  <div className="acoes-card-score" style={{ color, flexShrink: 0 }}>
                    <ScoreRing score={f.score} size={48} color={color} />
                    <span className="acoes-score-lbl">{label}</span>
                  </div>
                </div>

                {/* Indicadores específicos de FII */}
                <div className="fii-indicators">
                  <div className="fii-ind-item">
                    <span className="fii-ind-label">DY</span>
                    <span className="fii-ind-value" style={{ color: '#00C853' }}>{f.dy}</span>
                  </div>
                  <div className="fii-ind-item">
                    <span className="fii-ind-label">P/VP</span>
                    <span className="fii-ind-value" style={{ color: f.pvp < 1 ? '#00C853' : '#FFD600' }}>
                      {f.pvp.toFixed(2)}
                    </span>
                  </div>
                  <div className="fii-ind-item">
                    <span className="fii-ind-label">Preço</span>
                    <span className="fii-ind-value">R$ {f.price.toFixed(2)}</span>
                  </div>
                  <div className="fii-ind-item">
                    <span className="fii-ind-label">Variação</span>
                    <span className={`fii-ind-value ${isUp ? 'change-up' : 'change-down'}`}>
                      {isUp ? '▲' : '▼'} {Math.abs(f.change).toFixed(2)}%
                    </span>
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      )}

      <p className="acoes-footer-note">
        Clique em qualquer FII para ver a análise completa.
        Dados atualizados diariamente após o fechamento do mercado.
      </p>
    </div>
  );
}
