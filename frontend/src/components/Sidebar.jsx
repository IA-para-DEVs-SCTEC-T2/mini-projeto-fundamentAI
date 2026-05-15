import {
  Home, TrendingUp, Building2, Heart, BookOpen, Activity,
} from 'lucide-react';

const NAV_ITEMS = [
  { id: 'home',       icon: Home,       label: 'Início' },
  { id: 'acoes',      icon: TrendingUp, label: 'Ações' },
  { id: 'fiis',       icon: Building2,  label: 'FIIs' },
  { id: 'favoritos',  icon: Heart,      label: 'Favoritos' },
  { id: 'aprendizado',icon: BookOpen,   label: 'Aprendizado' },
];

export default function Sidebar({ activeNav, onNav }) {
  return (
    <aside className="sidebar">
      {/* Logo compacto */}
      <div className="sidebar-logo">
        <Activity size={22} color="#22c55e" />
        <span className="sidebar-logo-text">FundamentAI</span>
      </div>

      <nav className="sidebar-nav">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = activeNav === item.id;
          return (
            <button
              key={item.id}
              className={`sidebar-item ${isActive ? 'sidebar-item-active' : ''}`}
              onClick={() => onNav(item.id)}
              title={item.label}
            >
              <Icon size={19} />
              <span className="sidebar-label">{item.label}</span>
              {isActive && <span className="sidebar-active-bar" />}
            </button>
          );
        })}
      </nav>

      {/* Rodapé da sidebar */}
      <div className="sidebar-footer">
        <div className="sidebar-version">v0.1.0</div>
      </div>
    </aside>
  );
}
