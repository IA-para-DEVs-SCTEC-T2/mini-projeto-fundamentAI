import React, { useState, useEffect } from 'react';
import { Search, TrendingUp, TrendingDown, Activity, AlertCircle, Info, BarChart2, DollarSign, Briefcase } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts';
import { getTickerData, getAnalysis } from '../services/api';

const Analysis = () => {
  const [ticker, setTicker] = useState('PETR4');
  const [searchInput, setSearchInput] = useState('PETR4');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const [tickerData, setTickerData] = useState(null);
  const [analysisData, setAnalysisData] = useState(null);

  const fetchDashboardData = async (symbol) => {
    setLoading(true);
    setError(null);
    try {
      // Parallel requests for speed
      const [tickerRes, analysisRes] = await Promise.all([
        getTickerData(symbol),
        getAnalysis(symbol, 'haiku', true) // Using haiku for speed
      ]);
      
      setTickerData(tickerRes);
      setAnalysisData(analysisRes);
    } catch (err) {
      console.error(err);
      setError(err.detail || err.message || 'Erro ao carregar dados do ativo.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData(ticker);
  }, [ticker]);

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchInput.trim()) {
      setTicker(searchInput.toUpperCase().trim());
    }
  };

  if (loading) {
    return (
      <div className="loader-container">
        <div className="spinner"></div>
        <div className="glow-text">Processando Inteligência de Mercado...</div>
      </div>
    );
  }

  return (
    <div className="app-container">
      <header className="header">
        <div className="brand">
          <Activity size={28} color="#00e6d2" />
          FundamentAI
        </div>
      </header>

      <main className="main-content">
        <div className="search-container">
          <form onSubmit={handleSearch} className="search-box">
            <Search className="search-icon" size={20} />
            <input
              type="text"
              className="search-input"
              placeholder="Digite um Ticker (ex: VALE3)"
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
            />
            <button type="submit" className="search-btn">Analisar</button>
          </form>
        </div>

        {error && (
          <div className="card glass-panel" style={{ borderColor: 'var(--danger)', marginBottom: '2rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', color: 'var(--danger)' }}>
              <AlertCircle size={24} />
              <p>{error}</p>
            </div>
          </div>
        )}

        {tickerData && analysisData && !error && (
          <div className="dashboard">
            {/* Left Column: Summary & Metrics */}
            <div className="column-left" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              
              <div className="ticker-hero">
                <div>
                  <div className="ticker-name">{tickerData.ticker}</div>
                  <div className="ticker-sector">{tickerData.name || 'Empresa B3'} • {tickerData.sector || 'Setor Não Informado'}</div>
                </div>
                <div className="ticker-price-container">
                  <div className="ticker-price">R$ {tickerData.quote.current_price?.toFixed(2) || '---'}</div>
                  {tickerData.quote.change_percent && (
                    <div className={`ticker-change ${tickerData.quote.change_percent >= 0 ? 'change-up' : 'change-down'}`}>
                      {tickerData.quote.change_percent >= 0 ? <TrendingUp size={18} /> : <TrendingDown size={18} />}
                      {Math.abs(tickerData.quote.change_percent).toFixed(2)}%
                    </div>
                  )}
                </div>
              </div>

              <div className="card glass-panel">
                <div className="card-header">
                  <h3 className="card-title"><BarChart2 size={20}/> Indicadores Chave</h3>
                </div>
                <div className="metrics-grid">
                  <div className="metric-item">
                    <div className="metric-label">P/L</div>
                    <div className="metric-value">{tickerData.indicators.pe_ratio?.toFixed(2) || 'N/A'}</div>
                  </div>
                  <div className="metric-item">
                    <div className="metric-label">P/VP</div>
                    <div className="metric-value">{tickerData.indicators.pb_ratio?.toFixed(2) || 'N/A'}</div>
                  </div>
                  <div className="metric-item">
                    <div className="metric-label">ROE</div>
                    <div className="metric-value">{(tickerData.indicators.roe ? (tickerData.indicators.roe * 100).toFixed(2) : 'N/A')}%</div>
                  </div>
                  <div className="metric-item">
                    <div className="metric-label">Dívida/EBITDA</div>
                    <div className="metric-value">{tickerData.indicators.debt_ebitda?.toFixed(2) || 'N/A'}</div>
                  </div>
                </div>
              </div>

            </div>

            {/* Right Column: AI Analysis & Charts */}
            <div className="column-right" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              
              <div className="card glass-panel">
                <div className="card-header">
                  <h3 className="card-title"><Activity size={20}/> Diagnóstico da IA</h3>
                </div>
                
                <div className={`ai-verdict verdict-${analysisData.verdict.toLowerCase().includes('compra') ? 'compra' : analysisData.verdict.toLowerCase().includes('venda') ? 'venda' : 'neutro'}`}>
                  <div className="score-circle">
                    <span className="score-value">{analysisData.score.toFixed(1)}</span>
                    <span className="score-label">Score</span>
                  </div>
                  <div className="verdict-text">
                    <h3>Veredito: {analysisData.verdict}</h3>
                    <p>{analysisData.conclusion}</p>
                  </div>
                </div>

                <div className="points-grid">
                  <div>
                    <h4 style={{ color: 'var(--success)', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <TrendingUp size={16}/> Pontos Fortes
                    </h4>
                    <ul className="points-list positive">
                      {analysisData.positive_points.map((point, idx) => (
                        <li key={idx}>{point}</li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h4 style={{ color: 'var(--danger)', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <AlertCircle size={16}/> Pontos de Atenção
                    </h4>
                    <ul className="points-list negative">
                      {analysisData.negative_points.map((point, idx) => (
                        <li key={idx}>{point}</li>
                      ))}
                    </ul>
                  </div>
                </div>

                <div className="explanation-box">
                  <div className="explanation-title"><Info size={16}/> Momento Sugerido</div>
                  <div className="explanation-text">{analysisData.moment_suggestion || 'Nenhuma sugestão específica para o momento.'}</div>
                </div>
              </div>

              {tickerData.price_history && tickerData.price_history.length > 0 && (
                <div className="card glass-panel">
                  <div className="card-header">
                    <h3 className="card-title"><DollarSign size={20}/> Histórico de Preços (5 Anos)</h3>
                  </div>
                  <div className="chart-container">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={tickerData.price_history}>
                        <defs>
                          <linearGradient id="colorClose" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#00e6d2" stopOpacity={0.3}/>
                            <stop offset="95%" stopColor="#00e6d2" stopOpacity={0}/>
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" vertical={false} />
                        <XAxis 
                          dataKey="date" 
                          stroke="rgba(255,255,255,0.5)" 
                          tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 12 }}
                          tickFormatter={(val) => {
                            const date = new Date(val);
                            return `${date.getFullYear()}`;
                          }}
                          minTickGap={30}
                        />
                        <YAxis 
                          stroke="rgba(255,255,255,0.5)" 
                          tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 12 }}
                          domain={['auto', 'auto']}
                          tickFormatter={(val) => `R$ ${val}`}
                        />
                        <Tooltip 
                          contentStyle={{ backgroundColor: '#161a22', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '8px' }}
                          itemStyle={{ color: '#00e6d2' }}
                          labelStyle={{ color: '#8b949e', marginBottom: '0.5rem' }}
                        />
                        <Area type="monotone" dataKey="close" stroke="#00e6d2" strokeWidth={2} fillOpacity={1} fill="url(#colorClose)" />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              )}

            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default Analysis;
