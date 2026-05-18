function scoreClass(score) {
  if (score >= 75) return 'score-excellent';
  if (score >= 50) return 'score-good';
  if (score >= 25) return 'score-regular';
  return 'score-weak';
}

function scoreLabel(score) {
  if (score >= 75) return 'Excelente';
  if (score >= 50) return 'Bom';
  if (score >= 25) return 'Regular';
  return 'Fraco';
}

export function ScoreCircleLg({ score }) {
  const cls = scoreClass(score);
  return (
    <div className={`score-circle-lg ${cls}`}>
      <span className="score-num-lg">{Math.round(score)}</span>
      <span className="score-lbl">{scoreLabel(score)}</span>
    </div>
  );
}

export function ScoreCircleSm({ score }) {
  const cls = scoreClass(score);
  return (
    <div className={`score-circle-sm ${cls}`}>
      <span className="score-num-sm">{Math.round(score)}</span>
      <span className="score-lbl">Score</span>
    </div>
  );
}

export function ScoreBar({ score }) {
  const pct = Math.min(100, Math.max(0, score));
  return (
    <div className="score-bar-wrap" style={{ width: '100%' }}>
      <div className="score-bar-track">
        <div className="score-bar-thumb" style={{ left: `${pct}%` }} />
      </div>
      <div className="score-bar-labels">
        <span>Fraco</span>
        <span>Regular</span>
        <span>Bom</span>
        <span>Excelente</span>
      </div>
    </div>
  );
}

export default function ScoreCard({ score }) {
  return (
    <div className="card">
      <div className="card-header">
        <h3 className="card-title">Score Fundamentalista</h3>
      </div>
      <div className="score-card-body">
        <ScoreCircleLg score={score} />
        <ScoreBar score={score} />
      </div>
    </div>
  );
}
