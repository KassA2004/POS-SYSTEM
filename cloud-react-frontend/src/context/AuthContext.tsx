import React, { useState, useEffect, useCallback } from 'react';
import {
  api,
  extractErrorMessage,
  registerUnauthorizedHandler,
  getStoredToken,
  setStoredToken,
  clearStoredToken,
} from '../services/api';
import { AuthContext } from './AuthContextDef';
import type {
  User,
  TokenResponse,
  TenantRegistrationRequest,
  TenantRegistrationResponse,
  PaymentVerificationResponse,
} from '../types/auth';

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  // Starts true: we cannot know whether the stored token is still valid until
  // /auth/me answers, and rendering a redirect before then would bounce a
  // logged-in user to /login on every refresh.
  const [isLoading, setIsLoading] = useState<boolean>(() => Boolean(getStoredToken()));
  const [error, setError] = useState<string | null>(null);

  const isAuthenticated = !!user;

  const clearAuth = useCallback(() => {
    setUser(null);
    clearStoredToken();
  }, []);

  useEffect(() => {
    registerUnauthorizedHandler(clearAuth);
  }, [clearAuth]);

  // Session bootstrap: exchange the stored token for the authoritative user record.
  useEffect(() => {
    let cancelled = false;

    const bootstrap = async () => {
      if (!getStoredToken()) {
        setIsLoading(false);
        return;
      }
      try {
        const response = await api.get<User>('/auth/me');
        if (!cancelled) setUser(response.data);
      } catch {
        if (!cancelled) clearAuth();
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    };

    void bootstrap();
    return () => {
      cancelled = true;
    };
  }, [clearAuth]);

  const login = async (email: string, password: string): Promise<void> => {
    setError(null);
    try {
      const params = new URLSearchParams();
      params.append('username', email);
      params.append('password', password);

      const tokenResponse = await api.post<TokenResponse>('/auth/login', params, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });

      setStoredToken(tokenResponse.data.access_token);

      // Read the real identity back from the server rather than inventing one.
      const me = await api.get<User>('/auth/me');
      setUser(me.data);
    } catch (err: unknown) {
      clearStoredToken();
      const msg = extractErrorMessage(err);
      setError(msg);
      throw new Error(msg, { cause: err });
    }
  };

  const register = async (data: TenantRegistrationRequest): Promise<TenantRegistrationResponse> => {
    setError(null);
    try {
      const response = await api.post<TenantRegistrationResponse>('/auth/register', data);
      return response.data;
    } catch (err: unknown) {
      const msg = extractErrorMessage(err);
      setError(msg);
      throw new Error(msg, { cause: err });
    }
  };

  const verifyPayment = async (sessionId: string): Promise<PaymentVerificationResponse> => {
    setError(null);
    try {
      const response = await api.post<PaymentVerificationResponse>(`/auth/verify-payment/${sessionId}`);
      return response.data;
    } catch (err: unknown) {
      const msg = extractErrorMessage(err);
      setError(msg);
      throw new Error(msg, { cause: err });
    }
  };

  const logout = async (): Promise<void> => {
    setError(null);
    try {
      await api.post('/auth/logout');
    } catch {
      // Stateless tokens: a failed call must never trap the user in a session.
    } finally {
      clearAuth();
    }
  };

  const clearError = () => setError(null);

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated,
        isLoading,
        error,
        login,
        register,
        logout,
        verifyPayment,
        clearError,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
