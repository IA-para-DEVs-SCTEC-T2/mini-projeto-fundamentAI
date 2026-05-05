import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getTickerData = async (ticker, historyYears = 5) => {
  try {
    const response = await api.get(`/ticker/${ticker}?history_years=${historyYears}`);
    return response.data;
  } catch (error) {
    throw error.response?.data || error.message;
  }
};

export const getAnalysis = async (ticker, model = 'sonnet', useCache = true) => {
  try {
    const response = await api.post(`/analysis/${ticker}`, {
      model,
      use_cache: useCache,
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || error.message;
  }
};

export default api;
