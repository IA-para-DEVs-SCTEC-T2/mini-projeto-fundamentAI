import { Info } from 'lucide-react';

const TOOLTIPS = {
  pe_ratio:           'P/L — Preço dividido pelo Lucro por Ação. Quanto menor, mais barato em relação ao lucro.',
  pb_ratio:           'P/VP — Preço dividido pelo Valor Patrimonial. Abaixo de 1 indica desconto sobre o patrimônio.',
  roe:                'ROE — Retorno sobre Patrimônio Líquido. Mede a eficiência da empresa em gerar lucro.',
  debt_ebitda:        'Dívida/EBITDA — Nível de alavancagem. Quanto menor, menos endividada a empresa.',
  net_margin:         'Margem Líquida — % do faturamento que vira lucro. Quanto maior, mais eficiente.',
  dividend_yield:     'Dividend Yield — Rendimento distribuído em relação ao preço. Quanto maior, mais renda.',
  net_income_growth:  'Crescimento do Lucro YoY — CAGR do lucro líquido nos últimos anos.',
  div_growth:         'Crescimento de Dividendos YoY — CAGR dos dividendos anuais.',
};

function fmt(val, isPercent = false) {
  if (val === null || val === undefined) return 'N/A';
  if (isPercent) return `${(val * 100).toFixed(2)}%`;
  return typeof val === 'number' ? val.toFixed(2) : val;
}

function MetricItem({ label, value, tooltip }) {
  return (
    <div className="metric-item">
      <div className="metric-label">
        {label}
        {tooltip && (
          <span className="tooltip-wrapper" style={{ cursor: 'help' }}>
            <Info size={11} color="var(--text-muted)" />
            <span className="tooltip-box">{tooltip}</span>
          </span>
        )}
      </div>
      <div className="metric-value">{value}</div>
    </div>
  );
}

export default function IndicatorTable({ indicators, assetType }) {
  const isStock = assetType !== 'fii';

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="card-title">Indicadores Chave</h3>
        <span className={isStock ? 'badge-stock' : 'badge-fii'}>
          {isStock ? 'AÇÃO' : 'FII'}
        </span>
      </div>

      {isStock ? (
        <div className="metrics-grid" style={{ gridTemplateColumns: 'repeat(2,1fr)' }}>
          <MetricItem label="P/L"            value={fmt(indicators?.pe_ratio)}                          tooltip={TOOLTIPS.pe_ratio} />
          <MetricItem label="P/VP"           value={fmt(indicators?.pb_ratio)}                          tooltip={TOOLTIPS.pb_ratio} />
          <MetricItem label="ROE"            value={fmt(indicators?.roe, true)}                         tooltip={TOOLTIPS.roe} />
          <MetricItem label="Dívida/EBITDA"  value={fmt(indicators?.debt_ebitda)}                       tooltip={TOOLTIPS.debt_ebitda} />
          <MetricItem label="Margem Líquida" value={fmt(indicators?.net_margin, true)}                  tooltip={TOOLTIPS.net_margin} />
          <MetricItem label="Dividend Yield" value={fmt(indicators?.dividend_yield, true)}              tooltip={TOOLTIPS.dividend_yield} />
        </div>
      ) : (
        <>
          <div className="metrics-grid">
            <MetricItem label="P/VP"               value={fmt(indicators?.pb_ratio)}              tooltip={TOOLTIPS.pb_ratio} />
            <MetricItem label="P/L"                value={fmt(indicators?.pe_ratio)}              tooltip={TOOLTIPS.pe_ratio} />
            <MetricItem label="Dividend Yield"     value={fmt(indicators?.dividend_yield, true)}  tooltip={TOOLTIPS.dividend_yield} />
            <MetricItem label="Crescimento DY"     value={fmt(indicators?.div_growth, true)}      tooltip={TOOLTIPS.div_growth} />
          </div>
          <div className="fii-note">
            FIIs são avaliados com critérios específicos: foco em geração de renda e valor patrimonial.
          </div>
        </>
      )}
    </div>
  );
}
