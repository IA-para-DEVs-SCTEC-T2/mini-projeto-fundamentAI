import { useState } from 'react';
import { Search, Clock } from 'lucide-react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import Home from './pages/Home';
import Analysis from './pages/Analysis';
import Acoes from './pages/Acoes';
import Fiis from './pages/Fiis';
import Aprendizado from './pages/Aprendizado';
import NotFound from './pages/NotFound';
import ComingSoonToast from './components/ComingSoonToast';
import { useComingSoon } from './hooks/useComingSoon';
import { usePageTitle } from './hooks/usePageTitle';
import './index.css';

// Views mapeadas para páginas reais
const MAPPED_VIEWS = new Set(['home', 'analysis', 'acoes', 'fiis', 'aprendizado']);

const PAGE_TITLES = {
  home:        'Início',
  acoes:       'Ações',
  fiis:        'FIIs',
  aprendizado: 'Aprendizado',
  notfound:    'Em breve',
  analysis:    null, // título montado dinamicamente com o ticker
};

export default function App() {
  const [ticker, setTicker]   = useState(null);
  const [history, setHistory] = useState([]);
  const [view, setView]       = useState('home');   // 'home' | 'analysis' | 'acoes' | 'fiis' | 'aprendizado' | 'notfound'
  const [activeNav, setNav]   = useState('home');

  // Hook de "futura versão" — compartilhado entre todos os componentes via prop drilling
  const { showToast, hideToast, toastMessage } = useComingSoon();

  // Título dinâmico
  const pageTitle = view === 'analysis' && ticker
    ? ticker
    : PAGE_TITLES[view] ?? 'Início';
  usePageTitle(pageTitle);

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
    if (MAPPED_VIEWS.has(id)) {
      if (id === 'home') {
        setTicker(null);
        setView('home');
      } else {
        setView(id);
      }
    } else {
      // Qualquer nav não mapeada (ex: favoritos) → página de roadmap
      setView('notfound');
    }
  };

  const handleGoHome = () => {
    setTicker(null);
    setView('home');
    setNav('home');
  };

  return (
    <div className="app-shell">
      <Sidebar activeNav={activeNav} onNav={handleNav} />

      <div className="app-main">
        <Header
          onSearch={handleSearch}
          currentTicker={ticker || ''}
          showSearch={view === 'analysis'}
          onComingSoon={showToast}
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
              onComingSoon={showToast}
            />
          )}
          {view === 'notfound' && (
            <NotFound onHome={handleGoHome} />
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

      {/* Toast global de "futura versão" — renderizado no topo do DOM */}
      <ComingSoonToast message={toastMessage} onClose={hideToast} />
    </div>
  );
}
