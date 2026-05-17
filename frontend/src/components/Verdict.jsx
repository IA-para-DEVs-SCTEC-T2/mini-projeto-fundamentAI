import { TrendingUp, AlertCircle, Info } from 'lucide-react';
import { ScoreCircleSm } from './ScoreCard';

function verdictClass(verdict) {
  if (!verdict) return 'verdict-neutro';
  const v = verdict.toLowerCase();
  if (v.includes('positivo') || v.includes('favorável') || v.includes('compra') || v.includes('excelente') || v.includes('bom')) return 'verdict-positivo';
  if (v.includes('negativo') || v.includes('venda') || v.includes('fraco') || v.includes('desfavorável')) return 'verdict-negativo';
  return 'verdict-neutro';
}

export default function Verdict({ analysisData }) {
  if (!analysisData) return null;

  const cls = verdictClass(analysisData.verdict);

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="card-title"><Info size={18} /> Diagnóstico da IA</h3>
      </div>

      {/* Verdict block */}
      <div className={`ai-verdict ${cls}`}>
        <ScoreCircleSm score={analysisData.score} />
        <div className="verdict-text">
          <h3>Veredito: {analysisData.verdict}</h3>
          <p>{analysisData.conclusion}</p>
        </div>
      </div>

      {/* Points */}
      <div className="points-grid">
        <div>
          <h4 style={{ color: 'var(--success)', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.9rem' }}>
            <TrendingUp size={15} /> Pontos Fortes
          </h4>
          <ul className="points-list positive">
            {(analysisData.positive_points || []).map((p, i) => <li key={i}>{p}</li>)}
          </ul>
        </div>
        <div>
          <h4 style={{ color: 'var(--danger)', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.9rem' }}>
            <AlertCircle size={15} /> Pontos de Atenção
          </h4>
          <ul className="points-list negative">
            {(analysisData.negative_points || []).map((p, i) => <li key={i}>{p}</li>)}
          </ul>
        </div>
      </div>

      {/* Moment suggestion */}
      {analysisData.moment_suggestion && (
        <div className="moment-box">
          <div className="moment-label"><Info size={14} /> Momento Sugerido</div>
          <div className="moment-text">{analysisData.moment_suggestion}</div>
        </div>
      )}

      {/* Risk */}
      {analysisData.risk_assessment && (
        <div className="moment-box" style={{ borderLeftColor: 'var(--warning)', marginTop: '0.75rem' }}>
          <div className="moment-label" style={{ color: 'var(--warning)' }}>⚠ Avaliação de Risco</div>
          <div className="moment-text">{analysisData.risk_assessment}</div>
        </div>
      )}
    </div>
  );
}
