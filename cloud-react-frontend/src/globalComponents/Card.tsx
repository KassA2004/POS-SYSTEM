import type { ReactNode } from 'react';
import { cn } from '@/lib/cn';

export interface CardProps {
  title?: string;
  description?: string;
  actions?: ReactNode;
  children: ReactNode;
  className?: string;
  bodyClassName?: string;
}

/** Flat surface separated by a 1px border - no resting shadow (elevation e0). */
export function Card({ title, description, actions, children, className, bodyClassName }: CardProps) {
  return (
    <section className={cn('bg-surface border border-border-default rounded-lg', className)}>
      {(title || actions) && (
        <header className="flex items-start justify-between gap-4 p-6 pb-4 border-b border-border-subtle">
          <div className="min-w-0">
            {title && <h2 className="text-h3 font-semibold text-ink-primary">{title}</h2>}
            {description && <p className="text-caption text-ink-tertiary mt-1">{description}</p>}
          </div>
          {actions && <div className="flex items-center gap-2 shrink-0">{actions}</div>}
        </header>
      )}
      <div className={cn('p-6', bodyClassName)}>{children}</div>
    </section>
  );
}

export default Card;
