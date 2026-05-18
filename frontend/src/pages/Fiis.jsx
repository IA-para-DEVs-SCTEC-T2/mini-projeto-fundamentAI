import { useState } from 'react';
import { Building2, Search, ArrowRight } from 'lucide-react';

export default function Fiis({ onSearch }) {
  const [input, setInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    const val = input.trim().toUpperCase();
    if (val) onSearch(val);
  };

  return (
    <div className="acoes-page fiis-page">

      {/* Header */}
      <div className="acoes-header">
        <div className="acoes-header-left">
          <Building2 size={22} color="#8a2be2" />
          <div>
            <h1
              className="acoes-title"
              style={{
                background: 'linear-gradient(135deg, #fff 30%, #8a2be2)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              FIIs
            </h1>
            <p className="acoes-sub">Fundos de Investimento Imobiliário listados na B3</p>
          </div>
        </div>
      </div>

      {/* Busca */}
      <div className="home-search-wrap" style={{ marginTop: '1.5rem' }}>
        <form className="search-form" onSubmit={handleSubmit}>
          <Search className="search-icon-left" size={19} />
          <input
            className="search-input hero-search-input"
            placeholder="Digite o ticker do FII (ex: HGLG11, MXRF11, KNRI11)"
            value={input}
            onChange={(e) => setInput(e.target.value.toUpperCase())}
          />
          <button type="submit" className="search-btn hero-search-btn">
            Analisar <ArrowRight size={15} style={{ marginLeft: 4 }} />
          </button>
        </form>
      </div>

      <p className="acoes-footer-note" style={{ marginTop: '2rem' }}>
        Digite o ticker do FII para ver a análise completa com dados reais do backend.
        Dados atualizados diariamente após o fechamento do mercado.
      </p>

      <footer className="disclaimer">
        ⚠️ Esta análise é informativa e baseada em dados históricos públicos.
        Não constitui recomendação de investimento. A decisão final é sempre do usuário.
      </footer>
    </div>
  );
}
