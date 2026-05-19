import { useState } from 'react';
import { Search, ArrowRight, Zap } from 'lucide-react';

export default function Home({ onSearch }) {
  const [input, setInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    const val = input.trim().toUpperCase();
    if (val) onSearch(val);
  };

  return (
    <div className="home-dashboard">

      {/* ── Boas-vindas ── */}
      <div className="welcome-row">
        <div>
          <h1 className="welcome-title">
            Bem-vindo ao <span className="welcome-accent">FundamentAI</span>
          </h1>
          <p className="welcome-sub">
            Análise fundamentalista de ações e FIIs da B3 com Inteligência Artificial.
          </p>
        </div>
        <div className="welcome-badge">
          <Zap size={13} color="#22c55e" />
          <span>Dados atualizados diariamente</span>
        </div>
      </div>

      {/* ── Busca central ── */}
      <div className="home-search-wrap">
        <form className="search-form" onSubmit={handleSubmit}>
          <Search className="search-icon-left" size={19} />
          <input
            className="search-input hero-search-input"
            placeholder="Digite um Ticker (ex: PETR4, VALE3, HGLG11)"
            value={input}
            onChange={(e) => setInput(e.target.value.toUpperCase())}
          />
          <button type="submit" className="search-btn hero-search-btn">
            Analisar <ArrowRight size={15} style={{ marginLeft: 4 }} />
          </button>
        </form>
      </div>

      {/* ── Disclaimer ── */}
      <footer className="disclaimer">
        ⚠️ Esta análise é informativa e baseada em dados históricos públicos.
        Não constitui recomendação de investimento. A decisão final é sempre do usuário.
      </footer>
    </div>
  );
}
