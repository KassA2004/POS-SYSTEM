import axios, { AxiosError } from 'axios';
import type { ApiErrorResponse } from '../types/auth';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
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
    const isAuthEndpoint =
      error.config?.url?.includes('/auth/login') ||
      error.config?.url?.includes('/auth/register') ||
      error.config?.url?.includes('/auth/me') ||
      error.config?.url?.includes('/auth/verify-payment') ||
      error.config?.url?.includes('/payment-success');

    if (error.response?.status === 401 && !isAuthEndpoint) {
      if (onUnauthorizedCallback) {
        onUnauthorizedCallback();
      }
      // Redirect to login if not already on /login page
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
