import type { ReactNode } from 'react';
import { cn } from '@/lib/cn';

export type BadgeVariant = 'neutral' | 'success' | 'warning' | 'danger' | 'info';

const variantStyles: Record<BadgeVariant, string> = {
  neutral: 'bg-surface-sunken text-ink-secondary border-border-subtle',
  success: 'bg-success-bg text-success-fg border-success-border',
  warning: 'bg-warning-bg text-warning-fg border-warning-border',
  danger:  'bg-danger-bg text-danger-fg border-danger-border',
  info:    'bg-info-bg text-info-fg border-info-border',
};

export interface StatusBadgeProps {
  variant?: BadgeVariant;
  icon?: ReactNode;
  children: ReactNode;
  className?: string;
}

export function StatusBadge({ variant = 'neutral', icon, children, className }: StatusBadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-caption font-medium border whitespace-nowrap',
        variantStyles[variant],
        className
      )}
    >
      {icon}
      <span>{children}</span>
    </span>
  );
}

export default StatusBadge;
