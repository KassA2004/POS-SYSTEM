import React, { useState, useEffect, useCallback } from 'react';
import { api, extractErrorMessage, registerUnauthorizedHandler } from '../services/api';
import { AuthContext } from './AuthContextDef';
import type {
  User,
  TenantRegistrationRequest,
  TenantRegistrationResponse,
  PaymentVerificationResponse,
} from '../types/auth';

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(() => {
    const storedUser = localStorage.getItem('cloud_pos_user');
    return storedUser ? JSON.parse(storedUser) : null;
  });
  const [isLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const isAuthenticated = !!user;

  const clearAuth = useCallback(() => {
    setUser(null);
    localStorage.removeItem('cloud_pos_user');
  }, []);

  useEffect(() => {
    registerUnauthorizedHandler(clearAuth);
  }, [clearAuth]);

  const login = async (email: string, password: string): Promise<void> => {
    setError(null);
    try {
      const params = new URLSearchParams();
      params.append('username', email);
      params.append('password', password);

      await api.post('/auth/login', params, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      const loggedUser: User = {
        id: 1,
        email,
        role: 'TENANT_OWNER',
        tenant_id: 1,
        schema_name: 'tenant_schema',
      };

      setUser(loggedUser);
      localStorage.setItem('cloud_pos_user', JSON.stringify(loggedUser));
    } catch (err: unknown) {
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
      // Ignore network errors during logout
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
