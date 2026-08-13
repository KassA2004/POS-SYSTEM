import axios, { AxiosError } from 'axios';
import type { ApiErrorResponse } from '../types/auth';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const TOKEN_STORAGE_KEY = 'cloud_pos_token';

export const getStoredToken = (): string | null => localStorage.getItem(TOKEN_STORAGE_KEY);
export const setStoredToken = (token: string) => localStorage.setItem(TOKEN_STORAGE_KEY, token);
export const clearStoredToken = () => localStorage.removeItem(TOKEN_STORAGE_KEY);

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// The backend issues a stateless JWT in the login response body and reads it back
// from the Authorization header (OAuth2PasswordBearer). Attach it on every request.
api.interceptors.request.use((config) => {
  const token = getStoredToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Callback listener for 401 unauthorized errors (used by AuthContext to clear state)
type UnauthorizedCallback = () => void;
let onUnauthorizedCallback: UnauthorizedCallback | null = null;

export const registerUnauthorizedHandler = (cb: UnauthorizedCallback) => {
  onUnauthorizedCallback = cb;
};

// Centralized Response Interceptor for global error handling
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiErrorResponse>) => {
    const url = error.config?.url ?? '';
    const isAuthEndpoint =
      url.includes('/auth/login') ||
      url.includes('/auth/register') ||
      url.includes('/auth/me') ||
      url.includes('/auth/verify-payment') ||
      url.includes('/payment-success');

    if (error.response?.status === 401 && !isAuthEndpoint) {
      clearStoredToken();
      if (onUnauthorizedCallback) {
        onUnauthorizedCallback();
      }
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

// Helper function to extract user-friendly error messages from backend Axios errors
export const extractErrorMessage = (error: unknown): string => {
  if (axios.isAxiosError(error)) {
    const axiosErr = error as AxiosError<ApiErrorResponse>;
    const detail = axiosErr.response?.data?.detail;

    if (typeof detail === 'string') {
      return detail;
    }
    if (Array.isArray(detail) && detail.length > 0) {
      return detail.map((err) => err.msg).join(', ');
    }
    if (axiosErr.response?.status === 401) {
      return 'Invalid credentials or expired session.';
    }
    if (axiosErr.response?.status === 403) {
      return 'Access denied. Schema owner privileges required.';
    }
    if (axiosErr.message) {
      return axiosErr.message;
    }
  }
  return 'An unexpected error occurred. Please try again.';
};
