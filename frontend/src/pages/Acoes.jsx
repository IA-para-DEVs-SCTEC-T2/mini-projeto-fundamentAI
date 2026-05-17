import { useState, useMemo } from 'react';
import { TrendingUp, Search, ArrowUpDown, X } from 'lucide-react';
import ScoreRing, { scoreLabel } from '../components/ScoreRing';
import AssetLogo from '../components/AssetLogo';

// ── Mock data expandido (Etapa 4 substitui por API) ─────────────────────────
const MOCK_ACOES = [
  { ticker: 'PETR4',  name: 'Petrobras PN N2',       sector: 'Petróleo',         price: 37.42, change: +6.69, score: 85 },
  { ticker: 'PETR3',  name: 'Petrobras ON N2',        sector: 'Petróleo',         price: 40.10, change: +5.90, score: 83 },
  { ticker: 'PRIO3',  name: 'PetroRio S.A.',          sector: 'Petróleo',         price: 44.50, change: +3.20, score: 81 },
  { ticker: 'CSAN3',  name: 'Cosan S.A.',             sector: 'Energia',          price: 18.70, change: -1.20, score: 54 },
  { ticker: 'VALE3',  name: 'Vale S.A.',              sector: 'Mineração',        price: 61.80, change: -0.54, score: 65 },
  { ticker: 'ITUB4',  name: 'Itaú Unibanco PN',       sector: 'Bancos',           price: 34.90, change: +0.87, score: 78 },
  { ticker: 'ITUB3',  name: 'Itaú Unibanco ON',       sector: 'Bancos',           price: 33.50, change: +0.60, score: 76 },
  { ticker: 'BBAS3',  name: 'Banco do Brasil',        sector: 'Bancos',           price: 28.15, change: +2.10, score: 74 },
  { ticker: 'BBDC4',  name: 'Bradesco PN',            sector: 'Bancos',           price: 14.80, change: -0.30, score: 62 },
  { ticker: 'BBDC3',  name: 'Bradesco ON',            sector: 'Bancos',           price: 14.20, change: -0.20, score: 61 },
  { ticker: 'SANB11', name: 'Santander Brasil UNT',   sector: 'Bancos',           price: 28.90, change: +1.10, score: 68 },
  { ticker: 'WEGE3',  name: 'WEG S.A.',               sector: 'Indústria',        price: 52.30, change: +1.20, score: 90 },
  { ticker: 'EMBR3',  name: 'Embraer S.A.',           sector: 'Aeronáutica',      price: 48.20, change: +2.50, score: 73 },
  { ticker: 'RENT3',  name: 'Localiza Rent a Car',    sector: 'Serviços',         price: 48.60, change: -1.10, score: 70 },
  { ticker: 'MGLU3',  name: 'Magazine Luiza',         sector: 'Varejo',           price:  8.45, change: -2.30, score: 32 },
  { ticker: 'LREN3',  name: 'Lojas Renner',           sector: 'Varejo',           price: 14.20, change: -0.90, score: 55 },
  { ticker: 'ABEV3',  name: 'Ambev S.A.',             sector: 'Bebidas',          price: 12.80, change: +0.40, score: 60 },
  { ticker: 'SUZB3',  name: 'Suzano S.A.',            sector: 'Papel e Celulose', price: 58.10, change: +1.80, score: 76 },
  { ticker: 'RADL3',  name: 'Raia Drogasil',          sector: 'Saúde',            price: 24.50, change: +0.60, score: 82 },
  { ticker: 'HAPV3',  name: 'Hapvida S.A.',           sector: 'Saúde',            price:  5.80, change: -1.70, score: 38 },
  { ticker: 'RDOR3',  name: "Rede D'Or",              sector: 'Saúde',            price: 28.40, change: +0.90, score: 67 },
  { ticker: 'EGIE3',  name: 'Engie Brasil',           sector: 'Energia',          price: 42.70, change: +0.30, score: 80 },
  { ticker: 'TAEE11', name: 'Taesa UNT',              sector: 'Energia',          price: 35.60, change: +0.15, score: 77 },
  { ticker: 'CMIG4',  name: 'Cemig PN',               sector: 'Energia',          price: 12.40, change: +0.80, score: 72 },
  { ticker: 'ELET3',  name: 'Eletrobras ON',          sector: 'Energia',          price: 38.90, change: -0.50, score: 58 },
  { ticker: 'EQTL3',  name: 'Equatorial Energia',     sector: 'Energia',          price: 32.80, change: +0.70, score: 79 },
  { ticker: 'VIVT3',  name: 'Telefônica Vivo',        sector: 'Telecom',          price: 52.10, change: +0.20, score: 75 },
  { ticker: 'TIMS3',  name: 'TIM S.A.',               sector: 'Telecom',          price: 17.80, change: +0.40, score: 69 },
  { ticker: 'RAIL3',  name: 'Rumo S.A.',              sector: 'Logística',        price: 22.30, change: +1.00, score: 71 },
  { ticker: 'CCRO3',  name: 'CCR S.A.',               sector: 'Logística',        price: 14.60, change: -0.40, score: 63 },
];

// ── Opções de ordenação ──────────────────────────────────────────────────────
const SORT_OPTIONS = [
  { value: 'score_desc',  label: '↓ Maior Score' },
  { value: 'score_asc',   label: '↑ Menor Score' },
  { value: 'change_desc', label: '↓ Maior Variação' },
  { value: 'change_asc',  label: '↑ Menor Variação' },
  { value: 'price_desc',  label: '↓ Maior Preço' },
  { value: 'price_asc',   label: '↑ Menor Preço' },
  { value: 'az',          label: 'A → Z (Ticker)' },
];

// ── Helpers ──────────────────────────────────────────────────────────────────
function scoreColor(score) {
  if (score >= 75) return '#00C853';
  if (score >= 50) return '#FFD600';
  return '#FF5252';
}

// ── Main component ────────────────────────────────────────────────────────────
export default function Acoes({ onSearch }) {
  const [query, setQuery]   = useState('');
  const [sector, setSector] = useState('Todos');
  const [sortBy, setSortBy] = useState('score_desc');

  const sectors = useMemo(() => {
    const s = [...new Set(MOCK_ACOES.map((a) => a.sector))].sort();
    return ['Todos', ...s];
  }, []);

  const filtered = useMemo(() => {
    let list = [...MOCK_ACOES];
    if (query.trim()) {
      const q = query.trim().toUpperCase();
      list = list.filter(
        (a) => a.ticker.includes(q) || a.name.toUpperCase().includes(q)
      );
    }
    if (sector !== 'Todos') {
      list = list.filter((a) => a.sector === sector);
    }
    list.sort((a, b) => {
      switch (sortBy) {
        case 'score_desc':  return b.score  - a.score;
        case 'score_asc':   return a.score  - b.score;
        case 'change_desc': return b.change - a.change;
        case 'change_asc':  return a.change - b.change;
        case 'price_desc':  return b.price  - a.price;
        case 'price_asc':   return a.price  - b.price;
        case 'az':          return a.ticker.localeCompare(b.ticker);
        default:            return 0;
      }
    });
    return list;
  }, [query, sector, sortBy]);

  const hasActiveFilters = sector !== 'Todos' || sortBy !== 'score_desc' || query.trim();

  const clearFilters = () => {
    setSector('Todos');
    setSortBy('score_desc');
    setQuery('');
  };

  return (
    <div className="acoes-page">

      {/* Header */}
      <div className="acoes-header">
        <div className="acoes-header-left">
          <TrendingUp size={22} color="#22c55e" />
          <div>
            <h1 className="acoes-title">Ações</h1>
            <p className="acoes-sub">Empresas listadas na B3 — análise fundamentalista</p>
          </div>
        </div>
        <div className="acoes-search-wrap">
          <div className="acoes-search-inner">
            <Search size={15} color="var(--text-muted)" style={{ flexShrink: 0 }} />
            <input
              className="acoes-search-input"
              placeholder="Buscar ticker ou empresa..."
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

      {/* Filtros */}
      <div className="acoes-filter-bar">
        <div className="acoes-sector-chips">
          {sectors.map((s) => (
            <button
              key={s}
              className={`acoes-sector-chip${sector === s ? ' acoes-sector-chip-active' : ''}`}
              onClick={() => setSector(s)}
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
        <span className="acoes-count-num">{filtered.length}</span>
        <span className="acoes-count-label">
          {filtered.length === 1 ? 'ação encontrada' : 'ações encontradas'}
          {sector !== 'Todos' && ` em ${sector}`}
        </span>
      </div>

      {/* Grid ou empty state */}
      {filtered.length === 0 ? (
        <div className="acoes-empty">
          <div className="acoes-empty-icon">🔍</div>
          <div className="acoes-empty-text">Nenhuma ação encontrada</div>
          <button className="acoes-clear-btn" onClick={clearFilters}>Limpar filtros</button>
        </div>
      ) : (
        <div className="acoes-grid">
          {filtered.map((a) => {
            const isUp  = a.change >= 0;
            const color = scoreColor(a.score);
            const label = scoreLabel(a.score);
            return (
              <button key={a.ticker} className="acoes-card" onClick={() => onSearch(a.ticker)}>
                <div className="acoes-card-top">
                  <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.6rem', minWidth: 0, flex: 1 }}>
                    <AssetLogo ticker={a.ticker} sector={a.sector} size={34} />
                    <div style={{ minWidth: 0 }}>
                      <div className="acoes-card-ticker">{a.ticker}</div>
                      <div className="acoes-card-name">{a.name}</div>
                      <div className="acoes-card-sector">{a.sector}</div>
                    </div>
                  </div>
                  <div className="acoes-card-score" style={{ color, flexShrink: 0 }}>
                    <ScoreRing score={a.score} size={52} color={color} />
                    <span className="acoes-score-lbl">{label}</span>
                  </div>
                </div>
                <div className="acoes-card-bottom">
                  <span className="acoes-card-price">R$ {a.price.toFixed(2)}</span>
                  <span className={`acoes-card-change ${isUp ? 'change-up' : 'change-down'}`}>
                    {isUp ? '▲' : '▼'} {Math.abs(a.change).toFixed(2)}%
                  </span>
                </div>
              </button>
            );
          })}
        </div>
      )}

      <p className="acoes-footer-note">
        Clique em qualquer ação para ver a análise completa.
        Dados atualizados diariamente após o fechamento do mercado.
      </p>
    </div>
  );
}
