import { useEffect, useState, useMemo } from 'react';
import {
  ArrowLeft, Star, Bell, Info, TrendingUp, TrendingDown, ChevronDown, X,
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

// ── Descrições dos ativos para o modal "Saiba mais" ──────────────────────────
const ASSET_INFO = {
  // Ações
  PETR4: { name: 'Petrobras PN N2', type: 'Ação', sector: 'Petróleo, Gás e Biocombustíveis', desc: 'A Petrobras é a maior empresa da América Latina por valor de mercado e uma das maiores produtoras de petróleo do mundo. Atua na exploração, produção, refino e distribuição de petróleo e gás. É controlada pelo governo federal brasileiro e opera principalmente no pré-sal, com reservas de classe mundial. Distribui dividendos expressivos e é referência em governança corporativa no setor de energia.', highlight: 'Maior produtora de petróleo do Brasil, com forte geração de caixa e dividendos históricos.' },
  PETR3: { name: 'Petrobras ON N2', type: 'Ação', sector: 'Petróleo, Gás e Biocombustíveis', desc: 'Ação ordinária da Petrobras, com direito a voto nas assembleias. Mesmos fundamentos da PETR4, porém com menor liquidez. Indicada para investidores que desejam participação nas decisões estratégicas da companhia.', highlight: 'Mesmos fundamentos da PETR4 com direito a voto.' },
  VALE3: { name: 'Vale S.A.', type: 'Ação', sector: 'Mineração', desc: 'A Vale é uma das maiores mineradoras do mundo, líder global na produção de minério de ferro e níquel. Opera em mais de 30 países e é fundamental para a cadeia siderúrgica global. Seus resultados são fortemente influenciados pelo preço das commodities e pela demanda chinesa. Possui histórico de dividendos robustos e é uma das ações mais negociadas da B3.', highlight: 'Líder mundial em minério de ferro, com forte exposição ao crescimento chinês.' },
  ITUB4: { name: 'Itaú Unibanco PN', type: 'Ação', sector: 'Bancos', desc: 'O Itaú Unibanco é o maior banco privado da América Latina por ativos totais. Atua em varejo, atacado, seguros e gestão de patrimônio. Reconhecido pela eficiência operacional e consistência nos resultados, mantém ROE acima de 20% ao ano. É referência em inovação digital no setor bancário brasileiro.', highlight: 'Maior banco privado da América Latina, com ROE consistentemente acima de 20%.' },
  ITUB3: { name: 'Itaú Unibanco ON', type: 'Ação', sector: 'Bancos', desc: 'Ação ordinária do Itaú Unibanco com direito a voto. Mesmos fundamentos sólidos da ITUB4, com menor liquidez no mercado secundário.', highlight: 'Mesmos fundamentos do Itaú com direito a voto.' },
  BBAS3: { name: 'Banco do Brasil', type: 'Ação', sector: 'Bancos', desc: 'O Banco do Brasil é o maior banco público do país e um dos maiores da América Latina. Tem forte presença no agronegócio, segmento em que é líder absoluto. Combina solidez de banco público com eficiência crescente. Historicamente distribui dividendos generosos e negocia com múltiplos descontados em relação aos pares privados.', highlight: 'Líder no agronegócio brasileiro, com dividendos generosos e múltiplos atrativos.' },
  BBDC4: { name: 'Bradesco PN', type: 'Ação', sector: 'Bancos', desc: 'O Bradesco é um dos maiores bancos privados do Brasil, com forte presença em seguros e previdência. Passa por processo de transformação digital e reestruturação operacional. Historicamente reconhecido pela capilaridade e pela base diversificada de clientes.', highlight: 'Um dos maiores bancos privados do Brasil, em processo de transformação digital.' },
  WEGE3: { name: 'WEG S.A.', type: 'Ação', sector: 'Indústria', desc: 'A WEG é uma das maiores fabricantes de equipamentos elétricos do mundo, com presença em mais de 135 países. Produz motores, geradores, transformadores e soluções de automação industrial. É considerada uma das melhores empresas da B3 por sua consistência de crescimento, margens elevadas e gestão exemplar. Referência em qualidade e inovação no setor industrial.', highlight: 'Uma das melhores empresas da B3, com crescimento consistente e presença global.' },
  EMBR3: { name: 'Embraer S.A.', type: 'Ação', sector: 'Aeronáutica', desc: 'A Embraer é a terceira maior fabricante de aviões comerciais do mundo, especializada em jatos regionais. Atua também em aviação executiva e defesa. Após superar a crise da pandemia, retomou crescimento com forte carteira de pedidos. É uma das poucas empresas brasileiras com presença global relevante em tecnologia de ponta.', highlight: '3ª maior fabricante de aviões do mundo, com forte recuperação pós-pandemia.' },
  RADL3: { name: 'Raia Drogasil', type: 'Ação', sector: 'Saúde', desc: 'A Raia Drogasil é a maior rede de farmácias do Brasil, com mais de 3.000 lojas. Combina crescimento orgânico acelerado com margens sólidas e gestão eficiente. O setor farmacêutico é considerado defensivo, com demanda resiliente em qualquer ciclo econômico. A empresa investe fortemente em digitalização e serviços de saúde.', highlight: 'Maior rede de farmácias do Brasil, com crescimento acelerado e setor defensivo.' },
  EGIE3: { name: 'Engie Brasil', type: 'Ação', sector: 'Energia', desc: 'A Engie Brasil é uma das maiores geradoras de energia elétrica do país, com foco em fontes renováveis (hidrelétricas, eólicas e solares). Subsidiária do grupo francês Engie, combina solidez financeira com previsibilidade de receitas por contratos de longo prazo. É reconhecida pelos dividendos consistentes e pela gestão conservadora.', highlight: 'Líder em energia renovável no Brasil, com dividendos consistentes e contratos de longo prazo.' },
  VIVT3: { name: 'Telefônica Vivo', type: 'Ação', sector: 'Telecom', desc: 'A Telefônica Vivo é a maior operadora de telecomunicações do Brasil, com liderança em telefonia móvel, fibra óptica e serviços digitais. Subsidiária do grupo espanhol Telefónica, distribui dividendos elevados e tem receitas previsíveis. Investe fortemente na expansão da rede 5G e em serviços B2B.', highlight: 'Maior operadora de telecom do Brasil, com dividendos elevados e expansão 5G.' },
  PRIO3: { name: 'PetroRio S.A.', type: 'Ação', sector: 'Petróleo', desc: 'A PetroRio é uma empresa independente de exploração e produção de petróleo, focada na revitalização de campos maduros offshore. Cresceu rapidamente por aquisições estratégicas e é reconhecida pela eficiência operacional e baixo custo de extração. É uma das empresas de maior crescimento na B3 nos últimos anos.', highlight: 'Empresa de petróleo independente com crescimento acelerado e baixo custo de extração.' },
  // FIIs
  HGLG11: { name: 'CSHG Logística', type: 'FII', sector: 'Logística', desc: 'O CSHG Logística é um dos maiores FIIs de logística do Brasil, gerido pelo Credit Suisse Hedging-Griffo. Investe em galpões logísticos de alto padrão, com inquilinos de grande porte como Amazon, DHL e Magazine Luiza. Possui contratos longos e baixa vacância, garantindo distribuição de rendimentos estável e crescente.', highlight: 'Um dos maiores FIIs de logística do Brasil, com inquilinos de alto padrão e baixa vacância.' },
  XPML11: { name: 'XP Malls', type: 'FII', sector: 'Shopping', desc: 'O XP Malls é um FII de shoppings centers gerido pela XP Asset. Possui participação em shoppings de alto padrão em grandes centros urbanos. Os rendimentos são variáveis conforme o desempenho do varejo, mas a gestão ativa e a qualidade dos ativos garantem consistência nos dividendos.', highlight: 'FII de shoppings premium com gestão ativa da XP Asset.' },
  MXRF11: { name: 'Maxi Renda', type: 'FII', sector: 'Papel', desc: 'O Maxi Renda é um FII de papel (CRI) gerido pela XP Asset, um dos mais populares do Brasil pela liquidez e pelo dividend yield elevado. Investe em Certificados de Recebíveis Imobiliários (CRI), com rendimentos atrelados ao CDI ou IPCA. É indicado para investidores que buscam renda mensal com menor volatilidade.', highlight: 'Um dos FIIs mais populares do Brasil, com alto DY e rendimentos atrelados ao CDI/IPCA.' },
  KNRI11: { name: 'Kinea Renda Imobiliária', type: 'FII', sector: 'Híbrido', desc: 'O Kinea Renda Imobiliária é um FII híbrido gerido pela Kinea (Itaú), com portfólio diversificado entre galpões logísticos e lajes corporativas. É um dos maiores FIIs do Brasil por patrimônio líquido e reconhecido pela gestão profissional e pela consistência nos rendimentos.', highlight: 'Um dos maiores FIIs do Brasil, com portfólio diversificado e gestão Kinea/Itaú.' },
  GGRC11: { name: 'GGR Covepi Renda', type: 'FII', sector: 'Logística', desc: 'O GGR Covepi Renda é um FII de logística com foco em galpões built-to-suit (construídos sob medida para o inquilino). Possui contratos atípicos de longo prazo, o que garante previsibilidade de receita e baixo risco de vacância. É indicado para investidores que buscam estabilidade nos rendimentos.', highlight: 'FII de logística com contratos atípicos de longo prazo e alta previsibilidade de renda.' },
  VISC11: { name: 'Vinci Shopping Centers', type: 'FII', sector: 'Shopping', desc: 'O Vinci Shopping Centers é um FII de shoppings gerido pela Vinci Partners. Possui participação em shoppings regionais e super-regionais em diversas cidades brasileiras. A gestão ativa busca otimizar o mix de lojas e aumentar o ABL (Área Bruta Locável) dos ativos.', highlight: 'FII de shoppings com gestão ativa da Vinci Partners e portfólio diversificado geograficamente.' },
  KNCR11: { name: 'Kinea Rendimentos', type: 'FII', sector: 'Papel', desc: 'O Kinea Rendimentos é um FII de papel gerido pela Kinea (Itaú), com foco em CRIs de alta qualidade. Os rendimentos são atrelados ao CDI, tornando-o atrativo em cenários de juros elevados. É um dos FIIs de papel mais sólidos do mercado pela qualidade da gestão e dos ativos.', highlight: 'FII de papel premium com rendimentos atrelados ao CDI e gestão Kinea/Itaú.' },
  XPLG11: { name: 'XP Log', type: 'FII', sector: 'Logística', desc: 'O XP Log é um FII de logística gerido pela XP Asset, com portfólio de galpões de alto padrão em localizações estratégicas. Possui inquilinos de grande porte e contratos de médio e longo prazo. É um dos FIIs de logística mais líquidos da B3.', highlight: 'FII de logística com alta liquidez, gerido pela XP Asset.' },
  BTLG11: { name: 'BTG Pactual Logística', type: 'FII', sector: 'Logística', desc: 'O BTG Pactual Logística é um FII de galpões logísticos gerido pelo BTG Pactual, um dos maiores bancos de investimento da América Latina. Possui portfólio de ativos de alto padrão com inquilinos sólidos. A gestão do BTG garante acesso a oportunidades exclusivas de aquisição.', highlight: 'FII de logística com a solidez e o acesso a negócios do BTG Pactual.' },
};

// Descrição genérica para tickers não mapeados
function getAssetInfo(ticker, name, sector, assetType) {
  if (ASSET_INFO[ticker]) return ASSET_INFO[ticker];
  const isFii = ticker && ticker.endsWith('11');
  return {
    name: name || ticker,
    type: assetType === 'fii' || isFii ? 'FII' : 'Ação',
    sector: sector || (isFii ? 'Fundos Imobiliários' : 'B3'),
    desc: `${name || ticker} é um ativo listado na B3 no setor de ${sector || (isFii ? 'Fundos Imobiliários' : 'mercado financeiro')}. O Score Fundamentalista consolida os principais indicadores financeiros em uma nota de 0 a 100, ponderando eficiência, lucratividade, endividamento e geração de renda. Consulte os indicadores detalhados nas abas abaixo para uma análise completa.`,
    highlight: `Ativo listado na B3 — consulte os indicadores para análise completa.`,
  };
}

// ── Score Modal ───────────────────────────────────────────────────────────────
function ScoreModal({ info, score, onClose }) {
  if (!info) return null;

  function scoreColor(s) {
    if (s >= 75) return '#00C853';
    if (s >= 50) return '#FFD600';
    return '#FF5252';
  }
  function scoreLabel(s) {
    if (s >= 75) return 'Excelente';
    if (s >= 50) return 'Bom';
    if (s >= 25) return 'Regular';
    return 'Fraco';
  }

  const color = scoreColor(score);

  return (
    <div className="score-modal-overlay" onClick={onClose}>
      <div className="score-modal" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="score-modal-header">
          <div>
            <div className="score-modal-type-badge">{info.type} · {info.sector}</div>
            <h2 className="score-modal-title">{info.name}</h2>
          </div>
          <button className="score-modal-close" onClick={onClose} aria-label="Fechar">
            <X size={18} />
          </button>
        </div>

        {/* Score visual */}
        <div className="score-modal-score-row">
          <div className="score-modal-score-circle" style={{ borderColor: color, color }}>
            <span className="score-modal-score-num">{Math.round(score)}</span>
            <span className="score-modal-score-lbl">{scoreLabel(score)}</span>
          </div>
          <div className="score-modal-highlight">
            <div className="score-modal-highlight-label">✦ Destaque</div>
            <div className="score-modal-highlight-text">{info.highlight}</div>
          </div>
        </div>

        {/* Descrição */}
        <div className="score-modal-desc">{info.desc}</div>

        {/* Score explanation */}
        <div className="score-modal-explanation">
          <div className="score-modal-exp-title">
            <Info size={14} /> Como o Score é calculado
          </div>
          <p className="score-modal-exp-text">
            O Score Fundamentalista consolida os principais indicadores do ativo em uma nota de 0 a 100,
            ponderando eficiência operacional, lucratividade, nível de endividamento e geração de renda.
            Cada indicador recebe um peso específico conforme o tipo de ativo (Ação ou FII).
          </p>
          <div className="score-modal-ranges">
            {[['75–100','Excelente','#00C853'],['50–74','Bom','#4CAF50'],['25–49','Regular','#FFD600'],['0–24','Fraco','#FF5252']].map(([r,l,c]) => (
              <div key={l} className="score-modal-range-item" style={{ borderColor: c }}>
                <span style={{ color: c, fontWeight: 700 }}>{r}</span>
                <span style={{ color: c }}>{l}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="score-modal-footer">
          ⚠️ Esta informação é educativa e não constitui recomendação de investimento.
        </div>
      </div>
    </div>
  );
}

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
  const [showScoreModal, setShowScoreModal] = useState(false);

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
      // Backend unavailable — use mock data with correct ticker info
      const isFii = symbol.endsWith('11');
      const knownInfo = ASSET_INFO[symbol];
      setTickerData({
        ...MOCK_DATA,
        ticker: symbol,
        name: knownInfo?.name || null,
        sector: knownInfo?.sector || null,
        segment: null,
        asset_type: isFii ? 'fii' : 'stock',
      });
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
          <button className="asset-score-about-link" onClick={() => setShowScoreModal(true)}>Saiba mais →</button>
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
              <button className="asset-details-btn" onClick={() => setShowScoreModal(true)}>
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

      {/* ── Score Modal ── */}
      {showScoreModal && (
        <ScoreModal
          info={getAssetInfo(tickerData.ticker || ticker, name, sector, asset_type)}
          score={analysisData.score}
          onClose={() => setShowScoreModal(false)}
        />
      )}
    </div>
  );
}
