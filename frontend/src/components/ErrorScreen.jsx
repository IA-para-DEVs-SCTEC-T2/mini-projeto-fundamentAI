import { AlertCircle, AlertTriangle, WifiOff } from 'lucide-react';

function detectErrorType(error) {
  if (!error) return 'generic';
  const msg = (typeof error === 'string' ? error : error.detail || error.message || '').toLowerCase();
  if (msg.includes('inativo') || msg.includes('inactive')) return 'inactive';
  if (msg.includes('não encontrado') || msg.includes('not found') || msg.includes('404')) return 'notfound';
  if (msg.includes('network') || msg.includes('conexão') || msg.includes('econnrefused') || msg.includes('timeout')) return 'network';
  return 'generic';
}

export default function ErrorScreen({ error, ticker, onRetry, onHome }) {
  const type = detectErrorType(error);
  const rawMsg = typeof error === 'string' ? error : error?.detail || error?.message || 'Erro desconhecido.';

  if (type === 'notfound') {
    return (
      <div className="error-page">
        <div className="error-card">
          <div className="error-icon"><AlertCircle size={52} color="var(--danger)" /></div>
          <h2 className="error-title">Ticker não encontrado</h2>
          <p className="error-msg">
            O ticker <strong style={{ color: 'var(--text-main)' }}>{ticker || 'informado'}</strong> não foi encontrado na base de dados.
            Verifique se o código está correto.
          </p>
          <button className="btn-primary" onClick={onRetry}>Tentar novamente</button>
          <button className="btn-link" onClick={onHome}>← Voltar para a Home</button>
        </div>
      </div>
    );
  }

  if (type === 'inactive') {
    return (
      <div className="error-page">
        <div className="error-card">
          <div className="error-icon"><AlertTriangle size={52} color="var(--warning)" /></div>
          <h2 className="error-title" style={{ color: 'var(--warning)' }}>Ativo Inativo</h2>
          <p className="error-msg">
            O ativo <strong style={{ color: 'var(--text-main)' }}>{ticker || 'informado'}</strong> está classificado como inativo na B3
            e não possui dados suficientes para análise fundamentalista.
          </p>
          <div className="error-info">
            ℹ️ Ativos inativos possuem menos de 3 indicadores disponíveis e são excluídos automaticamente da análise.
          </div>
          <button className="btn-primary" onClick={onHome}>Buscar outro ativo</button>
        </div>
      </div>
    );
  }

  if (type === 'network') {
    return (
      <div className="error-page">
        <div className="error-card">
          <div className="error-icon"><WifiOff size={52} color="var(--danger)" /></div>
          <h2 className="error-title">Erro de conexão</h2>
          <p className="error-msg">
            Não foi possível conectar ao servidor. Verifique se o backend está rodando e tente novamente.
          </p>
          <div className="error-detail">{rawMsg}</div>
          <button className="btn-primary" onClick={onRetry}>Tentar novamente</button>
          <button className="btn-link" onClick={onHome}>← Voltar para a Home</button>
        </div>
      </div>
    );
  }

  // generic
  return (
    <div className="error-page">
      <div className="error-card">
        <div className="error-icon"><AlertCircle size={52} color="var(--danger)" /></div>
        <h2 className="error-title">Erro ao carregar dados</h2>
        <p className="error-msg">Ocorreu um erro ao processar a solicitação.</p>
        {rawMsg && <div className="error-detail">{rawMsg}</div>}
        <button className="btn-primary" onClick={onRetry}>Tentar novamente</button>
        <button className="btn-link" onClick={onHome}>← Voltar para a Home</button>
      </div>
    </div>
  );
}
