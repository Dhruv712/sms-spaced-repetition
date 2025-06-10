import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000', // adjust this if your backend is hosted elsewhere
  headers: {
    'Content-Type': 'application/json',
  },
});

// For debugging
api.interceptors.response.use(
  response => response,
  error => {
    console.error('API error:', error);
    return Promise.reject(error);
  }
);

export default api;
