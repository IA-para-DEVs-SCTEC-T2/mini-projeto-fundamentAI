import { useEffect, useRef } from 'react';

/**
 * ScoreRing — anel SVG animado com preenchimento progressivo ao montar.
 * Usado na Home (DashboardCard) e na tela de Ações.
 */

function scoreColor(score) {
  if (score >= 75) return '#00C853';
  if (score >= 50) return '#FFD600';
  return '#FF5252';
}

export function scoreLabel(score) {
  if (score >= 75) return 'Excelente';
  if (score >= 50) return 'Bom';
  if (score >= 25) return 'Regular';
  return 'Fraco';
}

export default function ScoreRing({ score, size = 54, color }) {
  const circleRef = useRef(null);
  const ringColor = color || scoreColor(score);
  const r         = (size - 7) / 2;
  const circ      = 2 * Math.PI * r;
  const targetDash = (Math.min(100, Math.max(0, score)) / 100) * circ;

  // Animação: parte de 0 e cresce até o valor real
  useEffect(() => {
    const el = circleRef.current;
    if (!el) return;

    el.style.strokeDasharray  = `0 ${circ}`;
    el.style.transition       = 'none';

    // Força reflow para garantir que a transição seja aplicada
    void el.getBoundingClientRect();

    el.style.transition       = 'stroke-dasharray 1s cubic-bezier(0.4, 0, 0.2, 1)';
    el.style.strokeDasharray  = `${targetDash} ${circ}`;
  }, [score, circ, targetDash]);

  return (
    <svg width={size} height={size} style={{ flexShrink: 0 }}>
      {/* Trilha de fundo */}
      <circle
        cx={size / 2} cy={size / 2} r={r}
        fill="none"
        stroke="rgba(255,255,255,0.1)"
        strokeWidth={6}
        transform={`rotate(-90 ${size / 2} ${size / 2})`}
      />
      {/* Arco colorido animado */}
      <circle
        ref={circleRef}
        cx={size / 2} cy={size / 2} r={r}
        fill="none"
        stroke={ringColor}
        strokeWidth={6}
        strokeLinecap="round"
        strokeDasharray={`0 ${circ}`}
        transform={`rotate(-90 ${size / 2} ${size / 2})`}
      />
      {/* Número central */}
      <text
        x={size / 2} y={size / 2 + 1}
        textAnchor="middle"
        dominantBaseline="central"
        fill={ringColor}
        fontSize={size * 0.26}
        fontWeight="800"
        fontFamily="Outfit, system-ui, sans-serif"
      >
        {Math.round(score)}
      </text>
    </svg>
  );
}
