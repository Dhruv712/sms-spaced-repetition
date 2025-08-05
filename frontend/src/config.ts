// API configuration
export const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

// Debug logging
console.log('Environment REACT_APP_API_BASE_URL:', process.env.REACT_APP_API_BASE_URL);
console.log('Using API_BASE_URL:', API_BASE_URL);

// Helper function to build API URLs
export const buildApiUrl = (endpoint: string): string => {
  const url = `${API_BASE_URL}${endpoint}`;
  console.log('Building API URL:', url);
  return url;
}; 