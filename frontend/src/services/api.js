import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const searchProducts = async (query) => {
  try {
    const response = await apiClient.post('/api/search', { query });
    return response.data;
  } catch (error) {
    console.error('API Error during product search:', error);
    const errorMessage = error.response?.data?.detail || 'Failed to connect to comparison server. Please try again.';
    throw new Error(errorMessage);
  }
};

export const getSearchHistory = async () => {
  try {
    const response = await apiClient.get('/api/history');
    return response.data;
  } catch (error) {
    console.error('API Error fetching search history:', error);
    throw new Error('Failed to fetch search history.');
  }
};

export const clearCache = async () => {
  try {
    const response = await apiClient.post('/api/cache/clear');
    return response.data;
  } catch (error) {
    console.error('API Error clearing cache:', error);
    throw new Error('Failed to clear database cache.');
  }
};
