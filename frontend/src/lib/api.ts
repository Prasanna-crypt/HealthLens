// Just a standard component, nothing fancy here.

import axios from 'axios';

// Get the API URL from environment variables, or default to relative in production / localhost in development
const API_BASE_URL =
  import.meta.env.VITE_API_URL !== undefined && import.meta.env.VITE_API_URL !== ''
    ? import.meta.env.VITE_API_URL
    : import.meta.env.PROD
    ? ''
    : 'http://localhost:8000';

// Create a pre-configured Axios instance
export const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  timeout: 120000, // Wait up to 2 minutes (needed because AI processing is slow)
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor: Runs BEFORE every API call
api.interceptors.request.use((config) => {
  // Get the saved login token from the browser's storage
  const token = localStorage.getItem('healthlens_token');
  
  // If we have a token, attach it to the request headers for authentication
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response Interceptor: Runs AFTER every API call returns
api.interceptors.response.use(
  (response) => response, // If successful, just return the response
  (error) => {
    // If the server says "401 Unauthorized", our token is invalid or expired
    if (error.response?.status === 401) {
      localStorage.removeItem('healthlens_token'); // Clear bad token
      window.location.href = '/login'; // Force user back to login page
    }
    return Promise.reject(error);
  }
);

// ─── Auth API Functions ─────────────────────────────────────────────────────
// Handles user login, registration, and getting user details
export const authAPI = {
  login: (username: string, password: string) => {
    // OAuth2 requires form data, not JSON
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    return api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
  },
  register: (email: string, password: string, full_name: string) =>
    api.post('/auth/register', { email, password, full_name }),
  getMe: () => api.get('/auth/me'),
};

// ─── Reports API Functions ──────────────────────────────────────────────────
// Handles uploading, fetching, comparing, and deleting lab reports
export const reportsAPI = {
  upload: (file: File, onProgress?: (progress: number) => void) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/reports/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 300000,
      onUploadProgress: (event) => {
        if (event.total && onProgress) {
          const percentage = Math.round((event.loaded * 100) / event.total);
          onProgress(percentage);
        }
      },
    });
  },
  extract: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/reports/extract', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 120000,
    });
  },
  save: (filename: string, results: any[]) => {
    return api.post('/reports/save', { filename, results }, {
      timeout: 300000,
    });
  },
  list: () => api.get('/reports/'),
  get: (id: number) => api.get(`/reports/${id}`),
  compare: (report1Id: number, report2Id: number) =>
    api.get(`/reports/compare?report1_id=${report1Id}&report2_id=${report2Id}`),
  delete: (id: number) => api.delete(`/reports/${id}`),
};

// ─── Results API Functions ──────────────────────────────────────────────────
// Fetches specific test results
export const resultsAPI = {
  get: (id: number) => api.get(`/results/${id}`),
  // encodeURIComponent ensures special characters in testName don't break the URL
  uniqueTests: () => api.get('/results/user/unique-tests'),
};

// ─── Demo API Functions ─────────────────────────────────────────────────────
// Loads sample data for demonstration purposes
export const demoAPI = {
  load: () => api.post('/demo/load'),
};
