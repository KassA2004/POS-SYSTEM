import type { ReactNode } from 'react';

export interface EmptyStateProps {
  icon?: ReactNode;
  title: string;
  /** Be specific and actionable - say what to do next, not just "no data". */
  message?: string;
  action?: ReactNode;
}

export function EmptyState({ icon, title, message, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center text-center py-16 gap-3">
      {icon && (
        <div className="w-12 h-12 rounded-full bg-surface-sunken text-ink-tertiary flex items-center justify-center">
          {icon}
        </div>
      )}
      <h3 className="text-h3 font-semibold text-ink-primary">{title}</h3>
      {message && <p className="text-body text-ink-secondary max-w-[420px]">{message}</p>}
      {action && <div className="mt-2">{action}</div>}
    </div>
  );
}

export default EmptyState;
