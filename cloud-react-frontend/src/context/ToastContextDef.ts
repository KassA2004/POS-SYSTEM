import { createContext } from 'react';

export type ToastVariant = 'success' | 'warning' | 'danger' | 'info';

export interface ToastMessage {
  id: number;
  variant: ToastVariant;
  message: string;
}

export interface ToastContextType {
  toast: (message: string, variant?: ToastVariant) => void;
  dismiss: (id: number) => void;
}

export const ToastContext = createContext<ToastContextType | undefined>(undefined);
