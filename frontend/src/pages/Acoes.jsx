import { useState } from 'react';
import { TrendingUp, Search, ArrowRight } from 'lucide-react';

export default function Acoes({ onSearch }) {
  const [input, setInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    const val = input.trim().toUpperCase();
    if (val) onSearch(val);
  };

  return (
    <div className="acoes-page">

      {/* Header */}
      <div className="acoes-header">
        <div className="acoes-header-left">
          <TrendingUp size={22} color="#22c55e" />
          <div>
            <h1 className="acoes-title">Ações</h1>
            <p className="acoes-sub">Empresas listadas na B3 — análise fundamentalista</p>
          </div>
        </div>
      </div>

      {/* Busca */}
      <div className="home-search-wrap" style={{ marginTop: '1.5rem' }}>
        <form className="search-form" onSubmit={handleSubmit}>
          <Search className="search-icon-left" size={19} />
          <input
            className="search-input hero-search-input"
            placeholder="Digite o ticker da ação (ex: PETR4, VALE3, WEGE3)"
            value={input}
            onChange={(e) => setInput(e.target.value.toUpperCase())}
          />
          <button type="submit" className="search-btn hero-search-btn">
            Analisar <ArrowRight size={15} style={{ marginLeft: 4 }} />
          </button>
        </form>
      </div>

      <p className="acoes-footer-note" style={{ marginTop: '2rem' }}>
        Digite o ticker da ação para ver a análise completa com dados reais do backend.
        Dados atualizados diariamente após o fechamento do mercado.
      </p>

      <footer className="disclaimer">
        ⚠️ Esta análise é informativa e baseada em dados históricos públicos.
        Não constitui recomendação de investimento. A decisão final é sempre do usuário.
      </footer>
    </div>
  );
}
