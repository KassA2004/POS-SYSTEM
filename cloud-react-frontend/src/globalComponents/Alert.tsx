import type { ReactNode } from 'react';
import { CircleCheck, CircleAlert, TriangleAlert, Info } from 'lucide-react';
import { cn } from '@/lib/cn';

export type AlertVariant = 'success' | 'warning' | 'danger' | 'info';

const styles: Record<AlertVariant, string> = {
  success: 'bg-success-bg text-success-fg border-success-border',
  warning: 'bg-warning-bg text-warning-fg border-warning-border',
  danger: 'bg-danger-bg text-danger-fg border-danger-border',
  info: 'bg-info-bg text-info-fg border-info-border',
};

const icons: Record<AlertVariant, typeof Info> = {
  success: CircleCheck,
  warning: TriangleAlert,
  danger: CircleAlert,
  info: Info,
};

export interface AlertProps {
  variant?: AlertVariant;
  title?: string;
  children: ReactNode;
  className?: string;
}

export function Alert({ variant = 'info', title, children, className }: AlertProps) {
  const Icon = icons[variant];
  const assertive = variant === 'danger' || variant === 'warning';

  return (
    <div
      role={assertive ? 'alert' : 'status'}
      className={cn('flex gap-3 rounded-lg border p-4', styles[variant], className)}
    >
      <Icon size={16} strokeWidth={1.5} aria-hidden="true" className="shrink-0 mt-0.5" />
      <div className="min-w-0 flex-1">
        {title && <p className="text-body font-medium">{title}</p>}
        <div className={cn('text-body-sm', title && 'mt-0.5')}>{children}</div>
      </div>
    </div>
  );
}

export default Alert;
