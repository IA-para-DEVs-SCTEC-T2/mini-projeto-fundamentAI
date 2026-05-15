import { useEffect, useState, useMemo } from 'react';
import {
  ArrowLeft, Star, Bell, Info, TrendingUp, TrendingDown, ChevronDown, BarChart2,
} from 'lucide-react';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';
import { getTickerData, getAnalysis } from '../services/api';
import LoadingScreen from '../components/LoadingScreen';
import IndicatorTable from '../components/IndicatorTable';
import Verdict from '../components/Verdict';
import Chart from '../components/Chart';
import '../analysis.css';

// ── Mock data fallback ──────────────────────────────────────────────────────

function generateMockPriceHistory() {
  const history = [];
  const now = new Date();
  let price = 32;
  for (let i = 365; i >= 0; i--) {
    const d = new Date(now);
    d.setDate(d.getDate() - i);
    price = Math.max(10, price + (Math.random() - 0.48) * 0.8);
    history.push({
      date: d.toISOString().slice(0, 10),
      close: parseFloat(price.toFixed(2)),
    });
  }
  return history;
}

const MOCK_DATA = {
  ticker: 'PETR4',
  name: 'Petrobras PN N2',
  sector: 'Petróleo, Gás e Biocombustíveis',
  segment: 'Exploração, Refino e Distribuição',
  asset_type: 'stock',
  quote: {
    current_price: 37.42,
    change_percent: 6.69,
    previous_close: 35.07,
    volume: 31200000,
    market_cap: 482700000000,
    week_52_low: 28.15,
    week_52_high: 44.90,
  },
  indicators: {
    pe_ratio: 6.72,
    roe: 0.184,
    net_margin: 0.217,
    dividend_yield: 0.121,
    ev_ebitda: 4.12,
    debt_ebitda: 0.68,
    pb_ratio: 0.9,
  },
  price_history: generateMockPriceHistory(),
};

const MOCK_ANALYSIS = {
  score: 85,
  verdict: 'Momento Favorável',
  conclusion:
    'Petrobras apresenta fundamentos sólidos com ROE acima da média setorial, dividend yield atrativo e baixo endividamento relativo ao EBITDA.',
  positive_points: [
    'ROE acima da média setorial',
    'Dividend Yield atrativo',
    'Baixo endividamento',
  ],
  negative_points: ['Sensível ao preço do petróleo', 'Risco político'],
  moment_suggestion:
    'Momento favorável para análise de entrada a longo prazo.',
  risk_assessment: 'Médio',
};

// ── Helpers ─────────────────────────────────────────────────────────────────

function fmtPrice(v) {
  if (v == null) return '---';
  return `R$ ${Number(v).toFixed(2)}`;
}

function fmtPct(v) {
  if (v == null) return '---';
  return `${Number(v).toFixed(2)}%`;
}

function fmtNum(v, decimals = 2) {
  if (v == null) return 'N/A';
  return Number(v).toFixed(decimals);
}

function fmtMarketCap(v) {
  if (v == null) return '---';
  if (v >= 1e12) return `R$ ${(v / 1e12).toFixed(2)} tri`;
  if (v >= 1e9)  return `R$ ${(v / 1e9).toFixed(2)} bi`;
  if (v >= 1e6)  return `R$ ${(v / 1e6).toFixed(2)} mi`;
  return `R$ ${v.toFixed(0)}`;
}

function fmtVolume(v) {
  if (v == null) return '---';
  if (v >= 1e9) return `${(v / 1e9).toFixed(1)}B`;
  if (v >= 1e6) return `${(v / 1e6).toFixed(1)}M`;
  if (v >= 1e3) return `${(v / 1e3).toFixed(1)}K`;
  return String(v);
}

function fmtDate(d) {
  if (!d) return '---';
  const dt = new Date(d);
  return dt.toLocaleDateString('pt-BR');
}

function fmtDateTime(d) {
  if (!d) {
    const now = new Date();
    return now.toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' });
  }
  return new Date(d).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' });
}

function scoreColor(score) {
  if (score >= 75) return '#00C853';
  if (score >= 50) return '#FFD600';
  return '#FF5252';
}

function scoreLabel(score) {
  if (score >= 75) return 'Excelente';
  if (score >= 50) return 'Bom';
  if (score >= 25) return 'Regular';
  return 'Fraco';
}

// ── Score Gauge SVG ──────────────────────────────────────────────────────────

function ScoreGauge({ score }) {
  const r = 54;
  const cx = 70;
  const cy = 70;
  const startAngle = 180;
  const endAngle = 0;
  const totalArc = 180;
  const pct = Math.min(100, Math.max(0, score)) / 100;
  const arcAngle = pct * totalArc;

  function polarToCartesian(angle) {
    const rad = ((angle - 180) * Math.PI) / 180;
    return {
      x: cx + r * Math.cos(rad),
      y: cy + r * Math.sin(rad),
    };
  }

  function describeArc(startDeg, endDeg) {
    const s = polarToCartesian(startDeg);
    const e = polarToCartesian(endDeg);
    const largeArc = endDeg - startDeg > 180 ? 1 : 0;
    return `M ${s.x} ${s.y} A ${r} ${r} 0 ${largeArc} 1 ${e.x} ${e.y}`;
  }

  const color = scoreColor(score);
  const label = scoreLabel(score);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.25rem' }}>
      <svg width="140" height="85" viewBox="0 0 140 85">
        {/* Background arc */}
        <path
          d={describeArc(0, 180)}
          fill="none"
          stroke="#2A2F36"
          strokeWidth="10"
          strokeLinecap="round"
        />
        {/* Colored arc */}
        {pct > 0 && (
          <path
            d={describeArc(0, arcAngle)}
            fill="none"
            stroke={color}
            strokeWidth="10"
            strokeLinecap="round"
          />
        )}
        {/* Score number */}
        <text
          x={cx}
          y={cy - 4}
          textAnchor="middle"
          fill="#FFFFFF"
          fontSize="26"
          fontWeight="800"
          fontFamily="Outfit, system-ui, sans-serif"
        >
          {Math.round(score)}
        </text>
        {/* Scale labels */}
        <text x="8"  y="82" fill="#A0A0A0" fontSize="9" fontFamily="Inter, sans-serif">0</text>
        <text x="125" y="82" fill="#A0A0A0" fontSize="9" fontFamily="Inter, sans-serif">100</text>
      </svg>
      <span className="score-gauge-classification" style={{ color }}>
        {label}
      </span>
    </div>
  );
}

// ── Indicator card ───────────────────────────────────────────────────────────

const IND_TOOLTIPS = {
  'P/L':            'Preço dividido pelo Lucro por Ação. Quanto menor, mais barato em relação ao lucro.',
  'ROE':            'Retorno sobre Patrimônio Líquido. Mede a eficiência em gerar lucro.',
  'Margem Líquida': '% do faturamento que vira lucro. Quanto maior, mais eficiente.',
  'DY':             'Dividend Yield — rendimento distribuído em relação ao preço.',
  'EV/EBITDA':      'Valor da empresa sobre geração de caixa. Quanto menor, mais barato.',
  'Dívida/PL':      'Nível de alavancagem financeira. Quanto menor, menos endividada.',
  'P/VP':           'Preço dividido pelo Valor Patrimonial. Abaixo de 1 indica desconto.',
  'Cresc. DY':      'Crescimento de Dividendos YoY — CAGR dos dividendos anuais.',
};

function classifyIndicator(key, value) {
  if (value == null) return null;
  const v = Number(value);
  switch (key) {
    case 'P/L':
      if (v > 0 && v <= 10) return 'excellent';
      if (v > 0 && v <= 20) return 'good';
      if (v > 0 && v <= 30) return 'regular';
      return 'weak';
    case 'ROE':
      if (v >= 0.20) return 'excellent';
      if (v >= 0.12) return 'good';
      if (v >= 0.06) return 'regular';
      return 'weak';
    case 'Margem Líquida':
      if (v >= 0.20) return 'excellent';
      if (v >= 0.10) return 'good';
      if (v >= 0.05) return 'regular';
      return 'weak';
    case 'DY':
      if (v >= 0.08) return 'excellent';
      if (v >= 0.05) return 'good';
      if (v >= 0.02) return 'regular';
      return 'weak';
    case 'EV/EBITDA':
      if (v > 0 && v <= 6)  return 'excellent';
      if (v > 0 && v <= 10) return 'good';
      if (v > 0 && v <= 15) return 'regular';
      return 'weak';
    case 'Dívida/PL':
    case 'Dívida/EBITDA':
      if (v <= 0.5) return 'excellent';
      if (v <= 1.0) return 'good';
      if (v <= 2.0) return 'regular';
      return 'weak';
    case 'P/VP':
      if (v > 0 && v <= 0.9) return 'excellent';
      if (v > 0 && v <= 1.2) return 'good';
      if (v > 0 && v <= 2.0) return 'regular';
      return 'weak';
    case 'Cresc. DY':
      if (v >= 0.08) return 'excellent';
      if (v >= 0.04) return 'good';
      if (v >= 0)    return 'regular';
      return 'weak';
    default:
      return 'good';
  }
}

const TAG_LABELS = {
  excellent: 'Excelente',
  good:      'Bom',
  regular:   'Regular',
  weak:      'Fraco',
};

function IndicatorCard({ title, value, desc, rawValue }) {
  const cls = classifyIndicator(title, rawValue);
  const tooltip = IND_TOOLTIPS[title];

  return (
    <div className="indicator-card">
      <div className="indicator-card-header">
        <span className="indicator-card-title">{title}</span>
        {tooltip && (
          <span className="ind-tooltip-wrapper">
            <Info size={13} color="#A0A0A0" />
            <span className="ind-tooltip-box">{tooltip}</span>
          </span>
        )}
      </div>
      <div className="indicator-card-value">{value}</div>
      <div className="indicator-card-desc">{desc}</div>
      {cls && (
        <span className={`indicator-tag indicator-tag-${cls}`}>
          {TAG_LABELS[cls]}
        </span>
      )}
    </div>
  );
}

// ── Period filter helper ─────────────────────────────────────────────────────

const PERIODS = ['1M', '6M', '1A', '5A', 'Máx'];

function filterHistory(history, period) {
  if (!history || history.length === 0) return [];
  const now = new Date();
  let cutoff;
  switch (period) {
    case '1M':  cutoff = new Date(now); cutoff.setMonth(cutoff.getMonth() - 1); break;
    case '6M':  cutoff = new Date(now); cutoff.setMonth(cutoff.getMonth() - 6); break;
    case '1A':  cutoff = new Date(now); cutoff.setFullYear(cutoff.getFullYear() - 1); break;
    case '5A':  cutoff = new Date(now); cutoff.setFullYear(cutoff.getFullYear() - 5); break;
    default:    return history;
  }
  return history.filter((d) => new Date(d.date) >= cutoff);
}

// ── Main component ───────────────────────────────────────────────────────────

export default function Analysis({ ticker, onSearch }) {
  const [loading, setLoading]       = useState(false);
  const [tickerData, setTickerData] = useState(null);
  const [analysisData, setAnalysis] = useState(null);
  const [activeTab, setActiveTab]   = useState('overview');
  const [period, setPeriod]         = useState('1A');

  const fetchData = async (symbol) => {
    setLoading(true);
    setTickerData(null);
    setAnalysis(null);
    try {
      const [td, ad] = await Promise.all([
        getTickerData(symbol),
        getAnalysis(symbol, 'haiku', true),
      ]);
      setTickerData(td);
      setAnalysis(ad);
    } catch {
      // Backend unavailable — use mock data
      setTickerData({ ...MOCK_DATA, ticker: symbol });
      setAnalysis(MOCK_ANALYSIS);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (ticker) {
      setActiveTab('overview');
      fetchData(ticker);
    }
  }, [ticker]);

  const filteredHistory = useMemo(
    () => filterHistory(tickerData?.price_history, period),
    [tickerData?.price_history, period],
  );

  if (loading) return <LoadingScreen ticker={ticker} />;
  if (!tickerData || !analysisData) return null;

  const { quote, indicators, asset_type, name, sector, segment } = tickerData;
  const isStock = asset_type !== 'fii';
  const price   = quote?.current_price;
  const change  = quote?.change_percent;
  const isUp    = (change ?? 0) >= 0;

  // Logo initials
  const logoText = (tickerData.ticker || ticker || '').slice(0, 2).toUpperCase();

  // Build indicator cards
  const stockCards = [
    { title: 'P/L',            value: fmtNum(indicators?.pe_ratio),              desc: 'Preço / Lucro',          raw: indicators?.pe_ratio },
    { title: 'ROE',            value: fmtNum((indicators?.roe ?? 0) * 100) + '%', desc: 'Retorno s/ Patrimônio', raw: indicators?.roe },
    { title: 'Margem Líquida', value: fmtNum((indicators?.net_margin ?? 0) * 100) + '%', desc: 'Eficiência operacional', raw: indicators?.net_margin },
    { title: 'DY',             value: fmtNum((indicators?.dividend_yield ?? 0) * 100) + '%', desc: 'Dividend Yield', raw: indicators?.dividend_yield },
    { title: 'EV/EBITDA',      value: fmtNum(indicators?.ev_ebitda),              desc: 'Valor / EBITDA',         raw: indicators?.ev_ebitda },
    { title: 'Dívida/PL',      value: fmtNum(indicators?.debt_ebitda),            desc: 'Alavancagem',            raw: indicators?.debt_ebitda },
  ];

  const fiiCards = [
    { title: 'P/VP',      value: fmtNum(indicators?.pb_ratio),                        desc: 'Preço / Valor Patrimonial', raw: indicators?.pb_ratio },
    { title: 'P/L',       value: fmtNum(indicators?.pe_ratio),                        desc: 'Preço / Lucro',             raw: indicators?.pe_ratio },
    { title: 'DY',        value: fmtNum((indicators?.dividend_yield ?? 0) * 100) + '%', desc: 'Dividend Yield',          raw: indicators?.dividend_yield },
    { title: 'Cresc. DY', value: fmtNum((indicators?.div_growth ?? 0) * 100) + '%',   desc: 'Crescimento Dividendos',    raw: indicators?.div_growth },
  ];

  const indCards = isStock ? stockCards : fiiCards;

  // Last date in history
  const lastDate = tickerData.price_history?.length
    ? tickerData.price_history[tickerData.price_history.length - 1]?.date
    : null;

  return (
    <div className="main-content">
      {/* 1. Sub-header */}
      <div className="analysis-subheader">
        <button className="analysis-back-btn" onClick={() => onSearch(null)}>
          <ArrowLeft size={15} />
          Voltar
        </button>
        <div className="analysis-header-actions">
          <button className="analysis-fav-btn">
            <Star size={14} />
            Adicionar aos favoritos
          </button>
          <button className="analysis-bell-btn" aria-label="Notificações">
            <Bell size={15} />
          </button>
        </div>
      </div>

      {/* 2. Asset identity block */}
      <div className="asset-identity-block">
        {/* Left */}
        <div className="asset-identity-left">
          <div className="asset-logo">{logoText}</div>
          <div className="asset-ticker-info">
            <div className="asset-ticker-row">
              <span className="asset-ticker-symbol">{tickerData.ticker || ticker}</span>
              <span className="asset-tag">{isStock ? 'Ação' : 'FII'}</span>
              <span className="asset-tag">B3</span>
            </div>
            {name && <div className="asset-full-name">{name}</div>}
            {(sector || segment) && (
              <div className="asset-sector-segment">
                {[sector, segment].filter(Boolean).join(' • ')}
              </div>
            )}
          </div>
        </div>

        {/* Center */}
        <div className="asset-score-center">
          <ScoreGauge score={analysisData.score} />
          <div className="score-gauge-label">
            <Info size={12} />
            Score Fundamentalista
          </div>
        </div>

        {/* Right */}
        <div className="asset-score-about">
          <div className="asset-score-about-title">Sobre o Score</div>
          <div className="asset-score-about-text">
            O Score Fundamentalista consolida os principais indicadores do ativo em uma nota de 0 a 100,
            ponderando eficiência, lucratividade, endividamento e geração de renda.
          </div>
          <button className="asset-score-about-link">Saiba mais →</button>
        </div>
      </div>

      {/* 3. Tabs */}
      <div className="analysis-tabs">
        {[
          { id: 'overview',    label: 'Visão Geral' },
          { id: 'indicators',  label: 'Indicadores' },
          { id: 'ai',          label: 'IA', badge: 'Novo' },
          { id: 'history',     label: 'Histórico' },
          { id: 'events',      label: 'Eventos' },
          { id: 'corp',        label: 'Corp. Action' },
        ].map((tab) => (
          <button
            key={tab.id}
            className={`analysis-tab${activeTab === tab.id ? ' analysis-tab-active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
            {tab.badge && <span className="tab-badge-new">{tab.badge}</span>}
          </button>
        ))}
      </div>

      {/* 4. Tab content */}
      {activeTab === 'overview' && (
        <>
          {/* 4a. Indicator cards */}
          <div className="indicator-cards-row">
            {indCards.map((c) => (
              <IndicatorCard
                key={c.title}
                title={c.title}
                value={c.value}
                desc={c.desc}
                rawValue={c.raw}
              />
            ))}
          </div>

          {/* 4b. Bottom grid */}
          <div className="analysis-bottom-grid">
            {/* Price chart */}
            <div className="price-chart-card">
              <div className="price-chart-header">
                <span className="price-chart-title">Histórico de Preço</span>
                <div className="price-chart-controls">
                  <div className="period-filters">
                    {PERIODS.map((p) => (
                      <button
                        key={p}
                        className={`period-btn${period === p ? ' period-btn-active' : ''}`}
                        onClick={() => setPeriod(p)}
                      >
                        {p}
                      </button>
                    ))}
                  </div>
                  <button className="compare-dropdown">
                    Comparar com <ChevronDown size={12} />
                  </button>
                </div>
              </div>

              <div className="price-current-row">
                <span className="price-current-value">{fmtPrice(price)}</span>
                {change != null && (
                  <span className={`price-current-change ${isUp ? 'price-change-up' : 'price-change-down'}`}>
                    {isUp ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
                    {isUp ? '+' : ''}{fmtPct(change)}
                  </span>
                )}
              </div>

              <div className="price-chart-area">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={filteredHistory} margin={{ top: 4, right: 4, left: 0, bottom: 0 }}>
                    <defs>
                      <linearGradient id="gradGreen" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%"  stopColor="#00C853" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#00C853" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" vertical={false} />
                    <XAxis
                      dataKey="date"
                      stroke="rgba(255,255,255,0.2)"
                      tick={{ fill: 'rgba(255,255,255,0.4)', fontSize: 10 }}
                      tickFormatter={(v) => {
                        const d = new Date(v);
                        if (period === '1M') return d.toLocaleDateString('pt-BR', { day: '2-digit', month: 'short' });
                        if (period === '6M') return d.toLocaleDateString('pt-BR', { month: 'short' });
                        return d.getFullYear();
                      }}
                      minTickGap={40}
                    />
                    <YAxis
                      stroke="rgba(255,255,255,0.2)"
                      tick={{ fill: 'rgba(255,255,255,0.4)', fontSize: 10 }}
                      domain={['auto', 'auto']}
                      tickFormatter={(v) => `R$${v}`}
                      width={55}
                    />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#161B22', borderColor: '#2A2F36', borderRadius: 8 }}
                      itemStyle={{ color: '#00C853' }}
                      labelStyle={{ color: '#A0A0A0', marginBottom: 4 }}
                      formatter={(v) => [`R$ ${Number(v).toFixed(2)}`, 'Preço']}
                      labelFormatter={(v) => new Date(v).toLocaleDateString('pt-BR')}
                    />
                    <Area
                      type="monotone"
                      dataKey="close"
                      stroke="#00C853"
                      strokeWidth={2}
                      fillOpacity={1}
                      fill="url(#gradGreen)"
                      dot={false}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>

              <div className="price-chart-footer">
                <span className="price-chart-footer-note">
                  <Info size={11} />
                  Dados referentes ao fechamento do mercado de {fmtDate(lastDate)}
                </span>
                <span className="price-chart-footer-update">
                  Atualizado em: {fmtDateTime(null)}
                </span>
              </div>
            </div>

            {/* Asset info */}
            <div className="asset-info-card">
              <div className="asset-info-title">Informações do Ativo</div>
              <div className="asset-info-list">
                <div className="asset-info-row">
                  <span className="asset-info-label">Preço atual</span>
                  <span className="asset-info-value">{fmtPrice(price)}</span>
                </div>
                <div className="asset-info-row">
                  <span className="asset-info-label">Variação (dia)</span>
                  <span className={`asset-info-value ${isUp ? 'asset-info-value-up' : 'asset-info-value-down'}`}>
                    {isUp ? '+' : ''}{fmtPct(change)}
                  </span>
                </div>
                <div className="asset-info-row">
                  <span className="asset-info-label">Mín. 52 semanas</span>
                  <span className="asset-info-value">{fmtPrice(quote?.week_52_low)}</span>
                </div>
                <div className="asset-info-row">
                  <span className="asset-info-label">Máx. 52 semanas</span>
                  <span className="asset-info-value">{fmtPrice(quote?.week_52_high)}</span>
                </div>
                <div className="asset-info-row">
                  <span className="asset-info-label">Valor de Mercado</span>
                  <span className="asset-info-value">{fmtMarketCap(quote?.market_cap)}</span>
                </div>
                <div className="asset-info-row">
                  <span className="asset-info-label">Volume médio (2M)</span>
                  <span className="asset-info-value">{fmtVolume(quote?.volume)}</span>
                </div>
                <div className="asset-info-row">
                  <span className="asset-info-label">Liquidez diária</span>
                  <span className="asset-info-value asset-info-value-high">Alta</span>
                </div>
              </div>
              <button className="asset-details-btn">
                Ver mais detalhes do ativo →
              </button>
            </div>
          </div>
        </>
      )}

      {activeTab === 'indicators' && (
        <IndicatorTable indicators={indicators} assetType={asset_type} />
      )}

      {activeTab === 'ai' && (
        <Verdict analysisData={analysisData} />
      )}

      {activeTab === 'history' && (
        <Chart priceHistory={tickerData.price_history} />
      )}

      {activeTab === 'events' && (
        <div className="tab-placeholder">
          <div className="tab-placeholder-icon">📅</div>
          <div>Eventos corporativos em breve</div>
        </div>
      )}

      {activeTab === 'corp' && (
        <div className="tab-placeholder">
          <div className="tab-placeholder-icon">🏢</div>
          <div>Corporate Actions em breve</div>
        </div>
      )}

      <footer className="disclaimer">
        Esta análise é informativa e baseada em dados históricos públicos.
        Não constitui recomendação de investimento. A decisão final é sempre do usuário.
      </footer>
    </div>
  );
}
