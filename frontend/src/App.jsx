import { useState } from 'react';
import { Search, Clock } from 'lucide-react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import Home from './pages/Home';
import Analysis from './pages/Analysis';
import Acoes from './pages/Acoes';
import Fiis from './pages/Fiis';
import Aprendizado from './pages/Aprendizado';
import './index.css';

export default function App() {
  const [ticker, setTicker]   = useState(null);
  const [history, setHistory] = useState([]);
  const [view, setView]       = useState('home');   // 'home' | 'analysis' | 'acoes' | 'fiis' | 'aprendizado'
  const [activeNav, setNav]   = useState('home');

  const handleSearch = (symbol) => {
    if (!symbol) {
      setTicker(null);
      setView('home');
      setNav('home');
      return;
    }
    const upper = symbol.toUpperCase().trim();
    setTicker(upper);
    setView('analysis');
    setHistory((prev) => {
      const filtered = prev.filter((t) => t !== upper);
      return [upper, ...filtered].slice(0, 5);
    });
  };

  const handleNav = (id) => {
    setNav(id);
    if (id === 'home') {
      setTicker(null);
      setView('home');
    } else if (id === 'acoes') {
      setView('acoes');
    } else if (id === 'fiis') {
      setView('fiis');
    } else if (id === 'aprendizado') {
      setView('aprendizado');
    } else {
      // favoritos → próximas etapas
      setView('home');
    }
  };

  return (
    <div className="app-shell">
      <Sidebar activeNav={activeNav} onNav={handleNav} />

      <div className="app-main">
        <Header
          onSearch={handleSearch}
          currentTicker={ticker || ''}
          showSearch={view === 'analysis'}
        />

        <div className="app-content">
          {view === 'home'        && <Home onSearch={handleSearch} />}
          {view === 'acoes'       && <Acoes onSearch={handleSearch} />}
          {view === 'fiis'        && <Fiis onSearch={handleSearch} />}
          {view === 'aprendizado' && (
            <Aprendizado
              ticker={ticker}
              onBack={() => setView(ticker ? 'analysis' : 'home')}
            />
          )}
          {view === 'analysis' && ticker && (
            <Analysis
              ticker={ticker}
              onSearch={handleSearch}
            />
          )}
        </div>
      </div>

      <nav className="bottom-nav">
        <button
          className={`bottom-nav-btn ${view === 'home' ? 'active' : ''}`}
          onClick={() => handleSearch(null)}
        >
          <Search size={20} />
          Início
        </button>
        {history.length > 0 && (
          <button
            className="bottom-nav-btn"
            onClick={() => handleSearch(history[0])}
          >
            <Clock size={20} />
            Recente
          </button>
        )}
      </nav>
    </div>
  );
}
