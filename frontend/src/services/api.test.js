import { describe, it, expect, vi, beforeEach } from 'vitest';
import api, { getTickerData, getAnalysis } from './api';

// Mock do axios
vi.mock('axios', () => {
  return {
    default: {
      create: vi.fn(() => ({
        get: vi.fn(),
        post: vi.fn()
      }))
    }
  };
});

describe('API Service', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('deve chamar getTickerData e retornar os dados corretamente', async () => {
    const mockData = { data: { ticker: 'PETR4', quote: { current_price: 35.5 } } };
    api.get.mockResolvedValueOnce(mockData);

    const result = await getTickerData('PETR4');
    
    expect(api.get).toHaveBeenCalledWith('/ticker/PETR4?history_years=5');
    expect(result).toEqual(mockData.data);
  });

  it('deve lidar com erro no getTickerData', async () => {
    const errorMessage = 'Erro ao buscar ticker';
    api.get.mockRejectedValueOnce({ response: { data: errorMessage } });

    await expect(getTickerData('INVALID')).rejects.toEqual(errorMessage);
  });

  it('deve chamar getAnalysis e retornar os dados corretamente', async () => {
    const mockData = { data: { verdict: 'Compra', score: 85 } };
    api.post.mockResolvedValueOnce(mockData);

    const result = await getAnalysis('PETR4', 'haiku', true);
    
    expect(api.post).toHaveBeenCalledWith('/analysis/PETR4', {
      model: 'haiku',
      use_cache: true
    });
    expect(result).toEqual(mockData.data);
  });
});
