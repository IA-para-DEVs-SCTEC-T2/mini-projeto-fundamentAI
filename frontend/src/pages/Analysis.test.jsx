import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import Analysis from './Analysis';
import * as apiService from '../services/api';

// Mock Recharts para evitar problemas com ResizeObserver no JSDOM
vi.mock('recharts', () => {
  const OriginalRecharts = vi.importActual('recharts');
  return {
    ...OriginalRecharts,
    ResponsiveContainer: ({ children }) => <div>{children}</div>,
    AreaChart: () => <div data-testid="area-chart" />,
    Area: () => null,
    XAxis: () => null,
    YAxis: () => null,
    CartesianGrid: () => null,
    Tooltip: () => null,
  };
});

// Mock da API
vi.mock('../services/api', () => ({
  getTickerData: vi.fn(),
  getAnalysis: vi.fn(),
}));

describe('Analysis Component', () => {
  const mockTickerData = {
    ticker: 'PETR4',
    name: 'Petrobras',
    sector: 'Petróleo e Gás',
    quote: { current_price: 35.5, change_percent: 2.5 },
    indicators: { pe_ratio: 3.5, pb_ratio: 1.2, roe: 0.35, debt_ebitda: 0.8 },
    price_history: [{ date: '2023-01-01', close: 30 }]
  };

  const mockAnalysisData = {
    verdict: 'Compra',
    score: 85,
    positive_points: ['Ponto positivo 1'],
    negative_points: ['Ponto negativo 1'],
    conclusion: 'Conclusão mockada',
    moment_suggestion: 'Sugestão mockada'
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('deve exibir estado de carregamento inicialmente', async () => {
    // Retarda as promessas para podermos ver o loading
    apiService.getTickerData.mockImplementation(() => new Promise(resolve => setTimeout(() => resolve(mockTickerData), 100)));
    apiService.getAnalysis.mockImplementation(() => new Promise(resolve => setTimeout(() => resolve(mockAnalysisData), 100)));

    render(<Analysis />);
    
    expect(screen.getByText(/Processando Inteligência de Mercado/i)).toBeInTheDocument();
  });

  it('deve renderizar os dados do ativo e análise após o carregamento', async () => {
    apiService.getTickerData.mockResolvedValue(mockTickerData);
    apiService.getAnalysis.mockResolvedValue(mockAnalysisData);

    render(<Analysis />);

    // Espera os dados carregarem
    await waitFor(() => {
      expect(screen.queryByText(/Processando Inteligência de Mercado/i)).not.toBeInTheDocument();
    });

    // Verifica Ticker Hero
    expect(screen.getByText('PETR4')).toBeInTheDocument();
    expect(screen.getByText('Petrobras • Petróleo e Gás')).toBeInTheDocument();
    expect(screen.getByText(/R\$ 35.50/)).toBeInTheDocument();

    // Verifica Veredito
    expect(screen.getByText(/Veredito: Compra/)).toBeInTheDocument();
    expect(screen.getByText('85.0')).toBeInTheDocument(); // Score
  });

  it('deve realizar uma nova busca ao submeter o formulário', async () => {
    apiService.getTickerData.mockResolvedValue(mockTickerData);
    apiService.getAnalysis.mockResolvedValue(mockAnalysisData);

    render(<Analysis />);

    // Espera os dados iniciais carregarem
    await waitFor(() => {
      expect(screen.queryByText(/Processando Inteligência de Mercado/i)).not.toBeInTheDocument();
    });

    // Digita um novo ticker e submete
    const input = screen.getByPlaceholderText(/Digite um Ticker/i);
    const button = screen.getByRole('button', { name: /Analisar/i });

    fireEvent.change(input, { target: { value: 'VALE3' } });
    fireEvent.click(button);

    // Verifica se as chamadas de API foram feitas com o novo ticker
    await waitFor(() => {
      expect(apiService.getTickerData).toHaveBeenCalledWith('VALE3');
      expect(apiService.getAnalysis).toHaveBeenCalledWith('VALE3', 'haiku', true);
    });
  });

  it('deve exibir mensagem de erro se a requisição falhar', async () => {
    const errorMessage = 'Ativo não encontrado';
    apiService.getTickerData.mockRejectedValue({ message: errorMessage });
    apiService.getAnalysis.mockRejectedValue({ message: errorMessage });

    render(<Analysis />);

    await waitFor(() => {
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });
  });
});
