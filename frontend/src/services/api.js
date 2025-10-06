import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_URL,
  timeout: 120000, // 2 minutes for model training
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      console.error('API Error:', error.response.data);
    } else if (error.request) {
      console.error('Network Error:', error.message);
    }
    return Promise.reject(error);
  }
);

// API methods
export const instrumentsAPI = {
  getAll: () => api.get('/instruments'),
  getInfo: (symbol) => api.get(`/instruments/${symbol}/info`),
  getHistorical: (symbol, params = {}) => 
    api.get(`/instruments/${symbol}/historical`, { params }),
};

export const forecastsAPI = {
  create: (data) => api.post('/forecast', data),
  getById: (forecastId) => api.get(`/forecast/${forecastId}`),
  getBySymbol: (symbol, limit = 10) => 
    api.get(`/forecasts/${symbol}`, { params: { limit } }),
  getModelPerformance: (symbol) => 
    api.get('/models/performance', { params: { symbol } }),
};

export default api;