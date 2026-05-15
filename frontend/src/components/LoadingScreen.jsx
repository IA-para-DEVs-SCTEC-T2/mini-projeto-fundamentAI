import { useEffect, useState } from 'react';
import { Database, BarChart2, Sparkles, CheckCircle } from 'lucide-react';

const STEPS = [
  { icon: Database,  label: 'Coletando dados da B3' },
  { icon: BarChart2, label: 'Calculando indicadores' },
  { icon: Sparkles,  label: 'Gerando análise com IA' },
];

export default function LoadingScreen({ ticker }) {
  const [activeStep, setActiveStep] = useState(0);

  useEffect(() => {
    const t1 = setTimeout(() => setActiveStep(1), 1200);
    const t2 = setTimeout(() => setActiveStep(2), 2600);
    return () => { clearTimeout(t1); clearTimeout(t2); };
  }, [ticker]);

  return (
    <div className="loader-page">
      <div className="spinner" />

      <div style={{ textAlign: 'center' }}>
        <div className="loader-title">Processando Inteligência de Mercado...</div>
        <div className="loader-sub" style={{ marginTop: '0.4rem' }}>
          Coletando dados, calculando indicadores e gerando análise via IA
        </div>
        {ticker && (
          <div style={{ marginTop: '0.5rem', color: 'var(--primary)', fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: '1.1rem' }}>
            {ticker}
          </div>
        )}
      </div>

      <div className="steps-row">
        {STEPS.map((step, idx) => {
          const Icon = step.icon;
          const isDone   = idx < activeStep;
          const isActive = idx === activeStep;
          return (
            <div key={idx} style={{ display: 'flex', alignItems: 'center' }}>
              <div className="step-item">
                <div className={`step-icon ${isDone ? 'done' : isActive ? 'active' : 'pending'}`}>
                  {isDone ? <CheckCircle size={20} /> : <Icon size={20} />}
                </div>
                <span className={`step-label ${isDone ? 'done-lbl' : isActive ? 'active-lbl' : ''}`}>
                  {step.label}
                </span>
              </div>
              {idx < STEPS.length - 1 && (
                <div className={`step-connector ${isDone ? 'done-line' : ''}`} />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
