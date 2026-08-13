export interface User {
  id: number;
  email: string;
  role: string;
  tenant_id: number;
  schema_name: string;
  tenant_name?: string | null;
}

export interface TenantRegistrationRequest {
  company_name: string;
  email: string;
  password: string;
}

export interface TenantRegistrationResponse {
  tenant_id: number;
  company_name: string;
  schema_name: string;
  state: number; // 0 = pending, 1 = active
  checkout_url?: string;
  session_id?: string;
  message: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface PaymentVerificationResponse {
  status: string;
  message: string;
  tenant: {
    id: number;
    name: string;
    schema_name: string;
    state: number;
  };
}

export interface ApiErrorResponse {
  detail: string | Array<{ loc: string[]; msg: string; type: string }>;
}

export interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (data: TenantRegistrationRequest) => Promise<TenantRegistrationResponse>;
  logout: () => Promise<void>;
  verifyPayment: (sessionId: string) => Promise<PaymentVerificationResponse>;
  clearError: () => void;
}
