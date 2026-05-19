import { Map, ArrowLeft, Rocket, Clock, Star } from 'lucide-react';

const ROADMAP_ITEMS = [
  { icon: Star,   label: 'Favoritos',              desc: 'Salve e acompanhe seus ativos preferidos.' },
  { icon: Clock,  label: 'Alertas de preço',        desc: 'Receba notificações quando um ativo atingir seu alvo.' },
  { icon: Rocket, label: 'Comparação de ativos',    desc: 'Compare dois ou mais ativos lado a lado.' },
];

/**
 * NotFound — exibida para qualquer view não mapeada.
 * Informa ao usuário que a página faz parte do roadmap e oferece retorno à Home.
 *
 * @param {function} onHome — callback para navegar de volta à raiz
 */
export default function NotFound({ onHome }) {
  return (
    <div className="notfound-page">
      <div className="notfound-card">

        {/* Ícone principal */}
        <div className="notfound-icon-wrap">
          <Map size={48} color="var(--primary)" strokeWidth={1.5} />
        </div>

        {/* Título e descrição */}
        <h1 className="notfound-title">Página em construção</h1>
        <p className="notfound-desc">
          Esta funcionalidade ainda não está disponível no MVP, mas já está no nosso
          roadmap de desenvolvimento. Em breve chegará por aqui!
        </p>

        {/* Roadmap preview */}
        <div className="notfound-roadmap">
          <div className="notfound-roadmap-label">
            <Rocket size={13} />
            Próximas funcionalidades
          </div>
          <ul className="notfound-roadmap-list">
            {ROADMAP_ITEMS.map((item) => {
              const Icon = item.icon;
              return (
                <li key={item.label} className="notfound-roadmap-item">
                  <div className="notfound-roadmap-icon">
                    <Icon size={15} />
                  </div>
                  <div>
                    <span className="notfound-roadmap-item-title">{item.label}</span>
                    <span className="notfound-roadmap-item-desc">{item.desc}</span>
                  </div>
                </li>
              );
            })}
          </ul>
        </div>

        {/* CTA */}
        <button className="notfound-home-btn" onClick={onHome}>
          <ArrowLeft size={15} />
          Voltar para o Início
        </button>
      </div>

      <footer className="disclaimer">
        ⚠️ Esta análise é informativa e baseada em dados históricos públicos.
        Não constitui recomendação de investimento. A decisão final é sempre do usuário.
      </footer>
    </div>
  );
}
