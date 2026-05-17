import { useState } from 'react';
import {
  ArrowLeft, BookOpen, TrendingUp, Building2, BarChart2,
  Star, Lightbulb, Target, ExternalLink, Info, ChevronRight,
  GraduationCap, Zap,
} from 'lucide-react';

// ── Dados educativos ─────────────────────────────────────────────────────────

const STOCK_INDICATORS = [
  {
    key: 'P/L', full: 'Preço / Lucro',
    desc: 'Quanto o mercado paga por R$1 de lucro da empresa. Quanto menor, mais barato o ativo.',
    ideal: 'Abaixo de 15x', formula: 'Preço ÷ Lucro por Ação',
    color: '#FF6D00', bg: 'rgba(255,109,0,0.1)', border: 'rgba(255,109,0,0.3)',
  },
  {
    key: 'ROE', full: 'Retorno sobre Patrimônio',
    desc: 'Mede a eficiência da empresa em gerar lucro com o dinheiro dos acionistas.',
    ideal: 'Acima de 15%', formula: 'Lucro Líquido ÷ Patrimônio Líquido × 100',
    color: '#2196F3', bg: 'rgba(33,150,243,0.1)', border: 'rgba(33,150,243,0.3)',
  },
  {
    key: 'Margem Líquida', full: 'Margem Líquida',
    desc: 'Percentual do faturamento que se converte em lucro após todos os custos.',
    ideal: 'Acima de 10%', formula: 'Lucro Líquido ÷ Receita Líquida × 100',
    color: '#7C3AED', bg: 'rgba(124,58,237,0.1)', border: 'rgba(124,58,237,0.3)',
  },
  {
    key: 'DY', full: 'Dividend Yield',
    desc: 'Rendimento em dividendos em relação ao preço atual. Indica a renda passiva gerada.',
    ideal: 'Acima de 5%', formula: 'Dividendos 12m ÷ Preço × 100',
    color: '#00C853', bg: 'rgba(0,200,83,0.1)', border: 'rgba(0,200,83,0.3)',
  },
  {
    key: 'EV/EBITDA', full: 'Valor da Empresa / EBITDA',
    desc: 'Compara o valor total da empresa com sua geração de caixa operacional.',
    ideal: 'Abaixo de 10x', formula: 'Enterprise Value ÷ EBITDA',
    color: '#E65100', bg: 'rgba(230,81,0,0.1)', border: 'rgba(230,81,0,0.3)',
  },
  {
    key: 'Dívida/EBITDA', full: 'Alavancagem Financeira',
    desc: 'Mede quantos anos de geração de caixa seriam necessários para pagar toda a dívida.',
    ideal: 'Abaixo de 2x', formula: 'Dívida Líquida ÷ EBITDA',
    color: '#F44336', bg: 'rgba(244,67,54,0.08)', border: 'rgba(244,67,54,0.25)',
  },
];

const FII_INDICATORS = [
  {
    key: 'P/VP', full: 'Preço / Valor Patrimonial',
    desc: 'Compara o preço de mercado com o valor real dos imóveis do fundo. Abaixo de 1 = desconto.',
    ideal: 'Abaixo de 1,0', formula: 'Preço da Cota ÷ VPA',
    color: '#7C3AED', bg: 'rgba(124,58,237,0.1)', border: 'rgba(124,58,237,0.3)',
  },
  {
    key: 'DY', full: 'Dividend Yield',
    desc: 'Rendimento mensal distribuído em relação ao preço da cota. Principal métrica de FIIs.',
    ideal: 'Acima de 0,8% ao mês', formula: 'Dividendo Mensal ÷ Preço × 100',
    color: '#00C853', bg: 'rgba(0,200,83,0.1)', border: 'rgba(0,200,83,0.3)',
  },
  {
    key: 'Cresc. DY', full: 'Crescimento de Dividendos',
    desc: 'Evolução dos dividendos ao longo do tempo. Fundos que crescem os dividendos são mais sólidos.',
    ideal: 'Positivo e crescente', formula: 'DY atual ÷ DY anterior − 1',
    color: '#2196F3', bg: 'rgba(33,150,243,0.1)', border: 'rgba(33,150,243,0.3)',
  },
  {
    key: 'Liquidez', full: 'Liquidez Diária',
    desc: 'Volume financeiro negociado por dia. Fundos com baixa liquidez são difíceis de vender.',
    ideal: 'Acima de R$ 1 milhão/dia', formula: 'Volume médio diário (R$)',
    color: '#FF6D00', bg: 'rgba(255,109,0,0.1)', border: 'rgba(255,109,0,0.3)',
  },
];

const FII_TYPES = [
  { name: 'Logística', icon: '🏭', desc: 'Galpões e centros de distribuição. Contratos longos, inquilinos sólidos.', color: '#FF6D00' },
  { name: 'Shopping', icon: '🛍️', desc: 'Shoppings centers. Renda variável com o desempenho do varejo.', color: '#2196F3' },
  { name: 'Escritórios', icon: '🏢', desc: 'Lajes corporativas. Sensível à vacância e ao mercado de trabalho.', color: '#7C3AED' },
  { name: 'Papel (CRI/CRA)', icon: '📄', desc: 'Investe em títulos de crédito imobiliário. Menor volatilidade.', color: '#00C853' },
  { name: 'Fundo de Fundos', icon: '📦', desc: 'Investe em cotas de outros FIIs. Diversificação automática.', color: '#E65100' },
];

const STOCK_TIPS = [
  { icon: Target, text: 'Analise pelo menos 3 anos de histórico antes de investir em uma ação.' },
  { icon: TrendingUp, text: 'Empresas com ROE consistente acima de 15% ao ano são raras e valiosas.' },
  { icon: Lightbulb, text: 'P/L baixo nem sempre significa barato — verifique se o lucro é recorrente.' },
  { icon: Star, text: 'Diversifique entre setores para reduzir o risco da carteira.' },
  { icon: Zap, text: 'Dívida/EBITDA acima de 3x é sinal de alerta — a empresa pode ter dificuldades.' },
];

const FII_TIPS = [
  { icon: Target, text: 'Prefira FIIs com P/VP abaixo de 1 — você compra o imóvel com desconto.' },
  { icon: TrendingUp, text: 'DY acima de 0,8% ao mês é considerado atrativo no cenário atual.' },
  { icon: Lightbulb, text: 'Verifique a vacância do fundo — imóveis vazios reduzem os dividendos.' },
  { icon: Star, text: 'Diversifique entre segmentos: logística, shopping, papel e escritórios.' },
  { icon: Zap, text: 'Liquidez diária abaixo de R$ 500 mil pode dificultar a venda das cotas.' },
];

const SCORE_RANGES = [
  { range: '75 – 100', label: 'Excelente', color: '#00C853', bg: 'rgba(0,200,83,0.1)', desc: 'Fundamentos excepcionais. Ativo com múltiplos indicadores acima da média.' },
  { range: '50 – 74',  label: 'Bom',       color: '#4CAF50', bg: 'rgba(76,175,80,0.1)',  desc: 'Bons fundamentos. Ativo sólido com alguns pontos de atenção.' },
  { range: '25 – 49',  label: 'Regular',   color: '#FFD600', bg: 'rgba(255,214,0,0.1)',  desc: 'Fundamentos medianos. Requer análise mais cuidadosa antes de investir.' },
  { range: '0 – 24',   label: 'Fraco',     color: '#FF5252', bg: 'rgba(255,82,82,0.1)',  desc: 'Fundamentos fracos. Alto risco — evite sem análise aprofundada.' },
];

const GLOSSARY = [
  { term: 'EBITDA', def: 'Lucro antes de juros, impostos, depreciação e amortização. Mede a geração de caixa operacional.' },
  { term: 'P/L', def: 'Preço da ação dividido pelo Lucro por Ação. Indica quantos anos levaria para recuperar o investimento.' },
  { term: 'ROE', def: 'Return on Equity — Lucro Líquido dividido pelo Patrimônio Líquido. Mede a eficiência da empresa.' },
  { term: 'ROIC', def: 'Return on Invested Capital — retorno sobre o capital total investido no negócio.' },
  { term: 'DY', def: 'Dividend Yield — dividendos pagos nos últimos 12 meses divididos pelo preço atual.' },
  { term: 'P/VP', def: 'Preço dividido pelo Valor Patrimonial por ação/cota. Abaixo de 1 indica desconto.' },
  { term: 'VPA', def: 'Valor Patrimonial por Ação — patrimônio líquido dividido pelo número de ações.' },
  { term: 'LPA', def: 'Lucro por Ação — lucro líquido dividido pelo número de ações em circulação.' },
  { term: 'EV', def: 'Enterprise Value — valor total da empresa (market cap + dívida líquida).' },
  { term: 'Free Float', def: 'Percentual das ações disponíveis para negociação no mercado.' },
  { term: 'Tag Along', def: 'Direito do acionista minoritário de vender suas ações pelo mesmo preço do controlador.' },
  { term: 'Novo Mercado', def: 'Segmento da B3 com as mais rígidas regras de governança corporativa.' },
  { term: 'Cotação', def: 'Preço atual de negociação de uma ação ou cota de FII na bolsa.' },
  { term: 'Liquidez', def: 'Facilidade de comprar ou vender um ativo sem impactar significativamente seu preço.' },
  { term: 'Vacância', def: 'Percentual de imóveis desocupados em um FII. Quanto menor, melhor.' },
  { term: 'Cap Rate', def: 'Taxa de capitalização — renda anual do imóvel dividida pelo seu valor de mercado.' },
  { term: 'Margem Líquida', def: 'Lucro Líquido dividido pela Receita Líquida. Mede a eficiência operacional.' },
  { term: 'Alavancagem', def: 'Uso de dívida para ampliar os retornos. Aumenta tanto ganhos quanto riscos.' },
  { term: 'CRI/CRA', def: 'Certificados de Recebíveis Imobiliários/Agrícolas — títulos de crédito lastreados em imóveis.' },
  { term: 'Dividend Payout', def: 'Percentual do lucro distribuído como dividendos. FIIs são obrigados a distribuir 95%.' },
];

const EXT_LINKS = [
  { name: 'Status Invest', url: 'https://statusinvest.com.br', desc: 'Análise completa de ações e FIIs com gráficos e histórico de dividendos.', color: '#2196F3', icon: '📊' },
  { name: 'Investidor10', url: 'https://investidor10.com.br', desc: 'Comparador de ativos, carteiras e rankings fundamentalistas.', color: '#FF6D00', icon: '🏆' },
  { name: 'Funds Explorer', url: 'https://fundsexplorer.com.br', desc: 'Especializado em FIIs — ranking, histórico de dividendos e comparações.', color: '#7C3AED', icon: '🏢' },
  { name: 'InfoMoney', url: 'https://infomoney.com.br', desc: 'Notícias, análises e educação financeira para investidores.', color: '#00C853', icon: '📰' },
  { name: 'Fundamentei', url: 'https://fundamentei.com', desc: 'Análise fundamentalista detalhada com dados históricos e comparações setoriais.', color: '#E65100', icon: '🔍' },
];

const TABS = [
  { id: 'acoes',       label: 'Ações',       icon: TrendingUp },
  { id: 'fiis',        label: 'FIIs',        icon: Building2 },
  { id: 'indicadores', label: 'Indicadores', icon: BarChart2 },
  { id: 'score',       label: 'Score',       icon: Star },
  { id: 'glossario',   label: 'Glossário',   icon: BookOpen },
];

// ── Sub-components ────────────────────────────────────────────────────────────

function IndicatorLearnCard({ ind }) {
  return (
    <div className="learn-ind-card" style={{ borderLeftColor: ind.color, background: ind.bg }}>
      <div className="learn-ind-header">
        <span className="learn-ind-key" style={{ color: ind.color }}>{ind.key}</span>
        <span className="learn-ind-full">{ind.full}</span>
      </div>
      <p className="learn-ind-desc">{ind.desc}</p>
      <div className="learn-ind-footer">
        <span className="learn-ind-formula">f(x) = {ind.formula}</span>
        <span className="learn-ind-ideal" style={{ color: ind.color, borderColor: ind.border, background: ind.bg }}>
          ✓ {ind.ideal}
        </span>
      </div>
    </div>
  );
}

function TipCard({ tips }) {
  return (
    <div className="learn-tips-grid">
      {tips.map((tip, i) => {
        const Icon = tip.icon;
        return (
          <div key={i} className="learn-tip-item">
            <div className="learn-tip-icon"><Icon size={16} /></div>
            <span className="learn-tip-text">{tip.text}</span>
          </div>
        );
      })}
    </div>
  );
}

// ── Main component ────────────────────────────────────────────────────────────

export default function Aprendizado({ ticker, onBack }) {
  const [activeTab, setActiveTab] = useState('acoes');

  return (
    <div className="aprendizado-page">

      {/* Header */}
      <div className="aprendizado-header">
        <div className="aprendizado-header-left">
          {onBack && (
            <button className="analysis-back-btn" onClick={onBack}>
              <ArrowLeft size={15} /> Voltar
            </button>
          )}
          <div className="aprendizado-title-wrap">
            <div className="aprendizado-title-row">
              <GraduationCap size={26} color="#2196F3" />
              <h1 className="aprendizado-title">Central de Aprendizado</h1>
            </div>
            <p className="aprendizado-sub">Aprenda a analisar ações e FIIs como um profissional</p>
          </div>
        </div>
        {ticker && (
          <div className="aprendizado-ticker-badge">
            <BookOpen size={13} />
            Aprendendo sobre: <strong>{ticker}</strong>
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="aprendizado-tabs">
        {TABS.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              className={`aprendizado-tab${activeTab === tab.id ? ' aprendizado-tab-active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <Icon size={15} />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* ── Tab: Ações ── */}
      {activeTab === 'acoes' && (
        <div className="aprendizado-content">
          <div className="learn-hero-card" style={{ background: 'linear-gradient(135deg, #0d1b2a 0%, #1565C0 60%, #0d47a1 100%)' }}>
            <div className="learn-hero-icon">📈</div>
            <div>
              <h2 className="learn-hero-title">O que são Ações?</h2>
              <p className="learn-hero-text">
                Ações são frações do capital social de uma empresa. Ao comprar uma ação, você se torna sócio
                e tem direito a participar dos lucros (dividendos) e da valorização do negócio.
                Na B3, existem dois tipos principais: <strong>ON</strong> (Ordinárias, com direito a voto)
                e <strong>PN</strong> (Preferenciais, com prioridade nos dividendos).
              </p>
            </div>
          </div>

          <h3 className="learn-section-title">Indicadores Fundamentalistas</h3>
          <div className="learn-ind-grid">
            {STOCK_INDICATORS.map((ind) => <IndicatorLearnCard key={ind.key} ind={ind} />)}
          </div>

          <h3 className="learn-section-title">💡 Dicas Práticas</h3>
          <TipCard tips={STOCK_TIPS} />
        </div>
      )}

      {/* ── Tab: FIIs ── */}
      {activeTab === 'fiis' && (
        <div className="aprendizado-content">
          <div className="learn-hero-card" style={{ background: 'linear-gradient(135deg, #1a0533 0%, #4C1D95 60%, #7C3AED 100%)' }}>
            <div className="learn-hero-icon">🏢</div>
            <div>
              <h2 className="learn-hero-title">O que são FIIs?</h2>
              <p className="learn-hero-text">
                Fundos de Investimento Imobiliário (FIIs) são fundos que investem em imóveis ou títulos imobiliários.
                São obrigados por lei a distribuir pelo menos <strong>95% do lucro semestral</strong> aos cotistas.
                Negociados na B3 como ações, com tickers terminados em <strong>11</strong> (ex: HGLG11, MXRF11).
              </p>
            </div>
          </div>

          <h3 className="learn-section-title">Indicadores de FIIs</h3>
          <div className="learn-ind-grid">
            {FII_INDICATORS.map((ind) => <IndicatorLearnCard key={ind.key} ind={ind} />)}
          </div>

          <h3 className="learn-section-title">🏗️ Tipos de FIIs</h3>
          <div className="learn-fii-types-grid">
            {FII_TYPES.map((t) => (
              <div key={t.name} className="learn-fii-type-card" style={{ borderTopColor: t.color }}>
                <div className="learn-fii-type-icon">{t.icon}</div>
                <div className="learn-fii-type-name" style={{ color: t.color }}>{t.name}</div>
                <div className="learn-fii-type-desc">{t.desc}</div>
              </div>
            ))}
          </div>

          <h3 className="learn-section-title">💡 Dicas para FIIs</h3>
          <TipCard tips={FII_TIPS} />
        </div>
      )}

      {/* ── Tab: Indicadores ── */}
      {activeTab === 'indicadores' && (
        <div className="aprendizado-content">
          <h3 className="learn-section-title" style={{ color: '#2196F3' }}>📊 Indicadores de Ações</h3>
          <div className="learn-table-wrap">
            <table className="learn-table">
              <thead>
                <tr>
                  <th>Indicador</th>
                  <th>Fórmula</th>
                  <th>Interpretação</th>
                  <th>Faixa Ideal</th>
                </tr>
              </thead>
              <tbody>
                {STOCK_INDICATORS.map((ind) => (
                  <tr key={ind.key}>
                    <td><span style={{ color: ind.color, fontWeight: 700 }}>{ind.key}</span></td>
                    <td className="learn-table-formula">{ind.formula}</td>
                    <td>{ind.desc}</td>
                    <td><span className="learn-table-ideal" style={{ color: ind.color }}>{ind.ideal}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <h3 className="learn-section-title" style={{ color: '#7C3AED', marginTop: '2rem' }}>🏢 Indicadores de FIIs</h3>
          <div className="learn-table-wrap">
            <table className="learn-table">
              <thead>
                <tr>
                  <th>Indicador</th>
                  <th>Fórmula</th>
                  <th>Interpretação</th>
                  <th>Faixa Ideal</th>
                </tr>
              </thead>
              <tbody>
                {FII_INDICATORS.map((ind) => (
                  <tr key={ind.key}>
                    <td><span style={{ color: ind.color, fontWeight: 700 }}>{ind.key}</span></td>
                    <td className="learn-table-formula">{ind.formula}</td>
                    <td>{ind.desc}</td>
                    <td><span className="learn-table-ideal" style={{ color: ind.color }}>{ind.ideal}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ── Tab: Score ── */}
      {activeTab === 'score' && (
        <div className="aprendizado-content">
          <div className="learn-hero-card" style={{ background: 'linear-gradient(135deg, #0a1628 0%, #1B5E20 60%, #00C853 100%)' }}>
            <div className="learn-hero-icon">🎯</div>
            <div>
              <h2 className="learn-hero-title">Score Fundamentalista FundamentAI</h2>
              <p className="learn-hero-text">
                O Score consolida os principais indicadores do ativo em uma nota de <strong>0 a 100</strong>,
                ponderando eficiência, lucratividade, endividamento e geração de renda.
                É calculado com pesos específicos para cada tipo de ativo (Ação ou FII).
              </p>
            </div>
          </div>

          <h3 className="learn-section-title">Faixas de Classificação</h3>
          <div className="learn-score-ranges">
            {SCORE_RANGES.map((r) => (
              <div key={r.label} className="learn-score-range-card" style={{ background: r.bg, borderColor: r.color }}>
                <div className="learn-score-range-num" style={{ color: r.color }}>{r.range}</div>
                <div className="learn-score-range-label" style={{ color: r.color }}>{r.label}</div>
                <div className="learn-score-range-desc">{r.desc}</div>
              </div>
            ))}
          </div>

          <h3 className="learn-section-title" style={{ marginTop: '2rem' }}>Pesos por Tipo de Ativo</h3>
          <div className="learn-weights-grid">
            <div className="learn-weights-card" style={{ borderTopColor: '#2196F3' }}>
              <h4 style={{ color: '#2196F3', marginBottom: '1rem' }}>📈 Ações</h4>
              {[['P/L','15%'],['ROE','20%'],['Dívida/EBITDA','15%'],['Margem Líquida','15%'],['EV/EBITDA','10%'],['Dividend Yield','10%'],['Crescimento Lucro','15%']].map(([k,v]) => (
                <div key={k} className="learn-weight-row">
                  <span>{k}</span>
                  <div className="learn-weight-bar-wrap">
                    <div className="learn-weight-bar" style={{ width: v, background: '#2196F3' }} />
                  </div>
                  <span style={{ color: '#2196F3', fontWeight: 700 }}>{v}</span>
                </div>
              ))}
            </div>
            <div className="learn-weights-card" style={{ borderTopColor: '#7C3AED' }}>
              <h4 style={{ color: '#7C3AED', marginBottom: '1rem' }}>🏢 FIIs</h4>
              {[['P/VP','30%'],['P/L','15%'],['Dividend Yield','35%'],['Crescimento DY','20%']].map(([k,v]) => (
                <div key={k} className="learn-weight-row">
                  <span>{k}</span>
                  <div className="learn-weight-bar-wrap">
                    <div className="learn-weight-bar" style={{ width: v, background: '#7C3AED' }} />
                  </div>
                  <span style={{ color: '#7C3AED', fontWeight: 700 }}>{v}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ── Tab: Glossário ── */}
      {activeTab === 'glossario' && (
        <div className="aprendizado-content">
          <div className="learn-hero-card" style={{ background: 'linear-gradient(135deg, #0d1117 0%, #1a1a2e 60%, #16213e 100%)' }}>
            <div className="learn-hero-icon">📚</div>
            <div>
              <h2 className="learn-hero-title">Glossário Financeiro</h2>
              <p className="learn-hero-text">
                Termos essenciais do mercado financeiro explicados de forma simples e direta.
              </p>
            </div>
          </div>
          <div className="learn-glossary-grid">
            {GLOSSARY.map((g) => (
              <div key={g.term} className="learn-glossary-item">
                <div className="learn-glossary-term">{g.term}</div>
                <div className="learn-glossary-def">{g.def}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Links externos */}
      <div className="learn-ext-section">
        <h3 className="learn-section-title">🔗 Aprofunde seu Conhecimento</h3>
        <div className="learn-links-grid">
          {EXT_LINKS.map((l) => (
            <a key={l.name} href={l.url} target="_blank" rel="noopener noreferrer" className="learn-link-card"
              style={{ borderTopColor: l.color }}>
              <div className="learn-link-icon">{l.icon}</div>
              <div className="learn-link-name" style={{ color: l.color }}>{l.name}</div>
              <div className="learn-link-desc">{l.desc}</div>
              <div className="learn-link-url">
                <ExternalLink size={11} /> {l.url.replace('https://', '')}
              </div>
            </a>
          ))}
        </div>
        <p className="learn-ext-disclaimer">
          <Info size={12} /> Links externos — o FundamentAI não se responsabiliza pelo conteúdo de terceiros.
        </p>
      </div>

      <footer className="disclaimer">
        Esta página tem fins exclusivamente educativos. Não constitui recomendação de investimento.
        A decisão final é sempre do usuário.
      </footer>
    </div>
  );
}
