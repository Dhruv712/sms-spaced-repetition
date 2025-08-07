// API configuration
export const API_BASE_URL = 'https://sms-spaced-repetition-production.up.railway.app';

// Debug logging
console.log('Environment REACT_APP_API_BASE_URL:', process.env.REACT_APP_API_BASE_URL);
console.log('Using API_BASE_URL:', API_BASE_URL);

// Helper function to build API URLs
export const buildApiUrl = (endpoint: string): string => {
  // Ensure we're always using HTTPS
  const baseUrl = API_BASE_URL.startsWith('https://') ? API_BASE_URL : `https://${API_BASE_URL.replace(/^https?:\/\//, '')}`;
  const url = `${baseUrl}${endpoint}`;
  console.log('Building API URL:', url);
  console.log('URL protocol:', new URL(url).protocol);
  console.log('URL hostname:', new URL(url).hostname);
  return url;
}; 