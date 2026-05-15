import { useState } from 'react';
import {
  Search, TrendingUp, TrendingDown,
  Database, Cpu, BarChart2,
  Activity, ArrowRight, Zap, ArrowUpRight,
  Heart, BarChart, Waves, Globe, Star,
} from 'lucide-react';
import { AreaChart, Area, ResponsiveContainer, Tooltip } from 'recharts';
import ScoreRing, { scoreLabel } from '../components/ScoreRing';

/* ── Filtros de análise ── */
const FILTERS = [
  { id: 'macro',       icon: Globe,    label: 'Macro' },
  { id: 'graficos',    icon: BarChart, label: 'Gráficos' },
  { id: 'volatilidade',icon: Waves,    label: 'Volatilidade' },
  { id: 'score',       icon: Star,     label: 'Score' },
  { id: 'dividendos',  icon: TrendingUp, label: 'Dividendos' },
];

/* ── Mais pesquisados ── */
const TRENDING = ['PETR4', 'VALE3', 'MXRF11', 'BBAS3', 'ITUB4', 'HGLG11'];

/* ── Ativos em destaque ── */
const FEATURED_ASSETS = [
  {
    ticker: 'PETR4',
    name: 'Petróleo Brasileiro S.A.',
    sector: 'Petróleo, Gás e Biocombustíveis',
    type: 'stock',
    price: 26.74,
    change: +1.45,
    score: 88,
    label: 'Excelente',
    indicators: { 'P/L': '6.8', 'ROE': '18,4%', 'DY': '8,3%', 'P/VP': '0.9' },
    sparkline: [24, 25, 24.5, 25.5, 25, 26, 25.8, 26.5, 26.2, 26.8, 26.5, 26.74],
    verdict: 'Momento Favorável',
    verdictType: 'positivo',
    gradient: 'linear-gradient(135deg, #4f1b8a 0%, #7c3aed 40%, #c026d3 100%)',
    accentColor: '#c084fc',
  },
  {
    ticker: 'VALE3',
    name: 'Vale S.A.',
    sector: 'Mineração',
    type: 'stock',
    price: 61.80,
    change: -0.54,
    score: 65,
    label: 'Bom',
    indicators: { 'P/L': '5.2', 'ROE': '22,1%', 'DY': '11,2%', 'P/VP': '1.1' },
    sparkline: [65, 63, 64, 62, 60, 61, 63, 62, 60, 61, 62, 61.80],
    verdict: 'Neutro',
    verdictType: 'neutro',
    gradient: 'linear-gradient(135deg, #7c2d12 0%, #ea580c 40%, #f59e0b 100%)',
    accentColor: '#fb923c',
  },
  {
    ticker: 'HGLG11',
    name: 'CSHG Logística FII',
    sector: 'Fundos Imobiliários',
    type: 'fii',
    price: 162.50,
    change: +0.31,
    score: 81,
    label: 'Excelente',
    indicators: { 'P/VP': '0.95', 'P/L': '12.3', 'DY': '9,8%', 'Cresc. DY': '+5,2%' },
    sparkline: [155, 157, 158, 156, 159, 160, 161, 160, 162, 161, 163, 162.50],
    verdict: 'Momento Favorável',
    verdictType: 'positivo',
    gradient: 'linear-gradient(135deg, #0c4a6e 0%, #0284c7 40%, #06b6d4 100%)',
    accentColor: '#38bdf8',
  },
  {
    ticker: 'ITUB4',
    name: 'Itaú Unibanco Holding',
    sector: 'Bancos',
    type: 'stock',
    price: 34.90,
    change: +0.87,
    score: 78,
    label: 'Bom',
    indicators: { 'P/L': '8.1', 'ROE': '20,5%', 'DY': '6,7%', 'P/VP': '1.8' },
    sparkline: [31, 32, 33, 32, 33, 34, 33, 34, 35, 34, 35, 34.90],
    verdict: 'Momento Favorável',
    verdictType: 'positivo',
    gradient: 'linear-gradient(135deg, #14532d 0%, #16a34a 40%, #4ade80 100%)',
    accentColor: '#4ade80',
  },
  {
    ticker: 'BBAS3',
    name: 'Banco do Brasil S.A.',
    sector: 'Bancos',
    type: 'stock',
    price: 28.15,
    change: +2.10,
    score: 74,
    label: 'Bom',
    indicators: { 'P/L': '4.9', 'ROE': '19,8%', 'DY': '9,1%', 'P/VP': '0.8' },
    sparkline: [25, 26, 25.5, 27, 26.5, 27.5, 27, 28, 27.8, 28.2, 28, 28.15],
    verdict: 'Momento Favorável',
    verdictType: 'positivo',
    gradient: 'linear-gradient(135deg, #831843 0%, #db2777 40%, #f472b6 100%)',
    accentColor: '#f472b6',
  },
  {
    ticker: 'MXRF11',
    name: 'Maxi Renda FII',
    sector: 'Fundos Imobiliários',
    type: 'fii',
    price: 10.42,
    change: +0.19,
    score: 70,
    label: 'Bom',
    indicators: { 'P/VP': '1.02', 'P/L': '10.8', 'DY': '12,1%', 'Cresc. DY': '+2,8%' },
    sparkline: [10, 10.1, 10.2, 10.1, 10.3, 10.2, 10.4, 10.3, 10.5, 10.4, 10.4, 10.42],
    verdict: 'Neutro',
    verdictType: 'neutro',
    gradient: 'linear-gradient(135deg, #1e3a5f 0%, #1d4ed8 40%, #60a5fa 100%)',
    accentColor: '#60a5fa',
  },
];

/* ── Helpers ── */
function scoreColor(score) {
  if (score >= 75) return '#22c55e';
  if (score >= 50) return '#4ade80';
  if (score >= 25) return '#f59e0b';
  return '#ef4444';
}
function verdictBg(t)     { return t === 'positivo' ? 'rgba(34,197,94,0.08)'  : t === 'negativo' ? 'rgba(239,68,68,0.08)'  : 'rgba(245,158,11,0.08)'; }
function verdictBorder(t) { return t === 'positivo' ? 'rgba(34,197,94,0.25)'  : t === 'negativo' ? 'rgba(239,68,68,0.25)'  : 'rgba(245,158,11,0.25)'; }
function verdictColor(t)  { return t === 'positivo' ? '#22c55e' : t === 'negativo' ? '#ef4444' : '#f59e0b'; }
function toSparkData(arr) { return arr.map((v, i) => ({ i, v })); }

/* ── Dashboard card ── */
function DashboardCard({ asset, onSearch }) {
  const isUp = asset.change >= 0;
  const accent = asset.accentColor;
  return (
    <div className="dash-card" onClick={() => onSearch(asset.ticker)} style={{ '--card-accent': accent }}>
      <div className="dash-card-gradient" style={{ background: asset.gradient }} />

      <div className="dash-card-header">
        <div className="dash-card-identity">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span className="dash-ticker">{asset.ticker}</span>
            <span className={asset.type === 'fii' ? 'badge-fii' : 'badge-stock'}>
              {asset.type === 'fii' ? 'FII' : 'AÇÃO'}
            </span>
          </div>
          <div className="dash-name">{asset.name}</div>
          <div className="dash-sector">{asset.sector}</div>
        </div>
        <div className="dash-card-score">
          <ScoreRing score={asset.score} size={52} color={accent} />
          <div className="dash-score-label" style={{ color: accent }}>{asset.label}</div>
        </div>
      </div>

      <div className="dash-price-row">
        <div>
          <div className="dash-price">R$ {asset.price.toFixed(2)}</div>
          <div className={`dash-change ${isUp ? 'change-up' : 'change-down'}`}>
            {isUp ? <TrendingUp size={13}/> : <TrendingDown size={13}/>}
            {isUp ? '+' : ''}{asset.change.toFixed(2)}%
          </div>
        </div>
        <div className="dash-sparkline">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={toSparkData(asset.sparkline)} margin={{ top:2, right:2, left:2, bottom:2 }}>
              <defs>
                <linearGradient id={`sg-${asset.ticker}`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor={accent} stopOpacity={0.35}/>
                  <stop offset="95%" stopColor={accent} stopOpacity={0}/>
                </linearGradient>
              </defs>
              <Tooltip
                contentStyle={{ background:'#111a14', border:`1px solid ${accent}40`, borderRadius:6, fontSize:11 }}
                itemStyle={{ color: accent }}
                formatter={(v) => [`R$ ${Number(v).toFixed(2)}`, '']}
                labelFormatter={() => ''}
              />
              <Area type="monotone" dataKey="v" stroke={accent} strokeWidth={1.8}
                fill={`url(#sg-${asset.ticker})`} dot={false}/>
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="dash-indicators">
        {Object.entries(asset.indicators).map(([k, v]) => (
          <div key={k} className="dash-ind-item">
            <div className="dash-ind-label">{k}</div>
            <div className="dash-ind-value" style={{ color: accent }}>{v}</div>
          </div>
        ))}
      </div>

      <div className="dash-verdict"
        style={{ background: verdictBg(asset.verdictType), borderColor: verdictBorder(asset.verdictType) }}>
        <span className="dash-verdict-dot" style={{ background: verdictColor(asset.verdictType) }}/>
        <span className="dash-verdict-text" style={{ color: verdictColor(asset.verdictType) }}>{asset.verdict}</span>
        <span className="dash-card-cta">
          Ver análise <ArrowUpRight size={12}/>
        </span>
      </div>
    </div>
  );
}

/* ── Main ── */
export default function Home({ onSearch, onFavorite }) {
  const [input, setInput]         = useState('');
  const [activeFilter, setFilter] = useState('score');
  const [favorites, setFavorites] = useState([]);

  const handleSubmit = (e) => {
    e.preventDefault();
    const val = input.trim().toUpperCase();
    if (val) onSearch(val);
  };

  const toggleFav = (ticker) => {
    setFavorites(prev =>
      prev.includes(ticker) ? prev.filter(t => t !== ticker) : [...prev, ticker]
    );
  };

  return (
    <div className="home-dashboard">

      {/* ── Boas-vindas ── */}
      <div className="welcome-row">
        <div>
          <h1 className="welcome-title">
            Bem-vindo ao <span className="welcome-accent">FundamentAI</span>
          </h1>
          <p className="welcome-sub">
            Análise fundamentalista de ações e FIIs da B3 com Inteligência Artificial.
          </p>
        </div>
        <div className="welcome-badge">
          <Zap size={13} color="#22c55e"/>
          <span>Dados atualizados diariamente</span>
        </div>
      </div>

      {/* ── Busca central ── */}
      <div className="home-search-wrap">
        <form className="search-form" onSubmit={handleSubmit}>
          <Search className="search-icon-left" size={19}/>
          <input
            className="search-input hero-search-input"
            placeholder="Digite um Ticker (ex: PETR4, VALE3, HGLG11)"
            value={input}
            onChange={(e) => setInput(e.target.value.toUpperCase())}
          />
          <button type="submit" className="search-btn hero-search-btn">
            Analisar <ArrowRight size={15} style={{ marginLeft:4 }}/>
          </button>
        </form>
      </div>

      {/* ── Filtros ── */}
      <div className="filter-row">
        {FILTERS.map((f) => {
          const Icon = f.icon;
          const active = activeFilter === f.id;
          return (
            <button
              key={f.id}
              className={`filter-btn ${active ? 'filter-btn-active' : ''}`}
              onClick={() => setFilter(f.id)}
            >
              <Icon size={14}/>
              {f.label}
            </button>
          );
        })}
      </div>

      {/* ── Cards de ativos ── */}
      <div className="section-header" style={{ marginTop: '0.5rem', width: '100%' }}>
        <Activity size={17} color="var(--primary)"/>
        <h2 className="section-title">Ativos em Destaque</h2>
      </div>

      <div className="dash-grid" style={{ width: '100%' }}>
        {FEATURED_ASSETS.map((a) => (
          <DashboardCard key={a.ticker} asset={a} onSearch={onSearch}/>
        ))}
      </div>

      {/* ── Rodapé da seção ── */}
      <div className="home-footer-section" style={{ width: '100%' }}>
        {/* Mais pesquisados */}
        <div className="trending-row">
          <span className="trending-label">Mais pesquisados:</span>
          {TRENDING.map((t) => (
            <button key={t} className="trending-chip" onClick={() => onSearch(t)}>
              +{t}
            </button>
          ))}
        </div>

        {/* Ações */}
        <div className="footer-actions">
          <button
            className="footer-action-btn fav-btn"
            onClick={() => toggleFav('PETR4')}
          >
            <Heart size={15} fill={favorites.includes('PETR4') ? '#f472b6' : 'none'}
              color={favorites.includes('PETR4') ? '#f472b6' : 'var(--text-muted)'}/>
            Adicionar aos favoritos
          </button>
          <button
            className="footer-action-btn home-btn"
            onClick={() => onSearch(null)}
          >
            ← Voltar para início
          </button>
        </div>
      </div>

      {/* ── Disclaimer ── */}
      <footer className="disclaimer">
        ⚠️ Esta análise é informativa e baseada em dados históricos públicos.
        Não constitui recomendação de investimento. A decisão final é sempre do usuário.
      </footer>
    </div>
  );
}
