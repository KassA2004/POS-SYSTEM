import type { ReactNode } from 'react';
import { Skeleton } from './Skeleton';
import { cn } from '@/lib/cn';

export interface StatTileProps {
  label: string;
  value?: string | number;
  icon?: ReactNode;
  subtext?: string;
  loading?: boolean;
  className?: string;
}

export function StatTile({ label, value, icon, subtext, loading, className }: StatTileProps) {
  return (
    <div className={cn('bg-surface border border-border-default rounded-lg p-5 flex flex-col gap-2', className)}>
      <div className="flex items-center justify-between">
        <span className="text-micro font-semibold uppercase tracking-[0.04em] text-ink-tertiary">{label}</span>
        {icon && <span className="text-ink-tertiary">{icon}</span>}
      </div>

      {loading ? (
        <Skeleton className="h-9 w-3/4 my-0.5" />
      ) : (
        <div className="text-display font-bold tabular-nums text-ink-primary tracking-[-0.02em]">
          {value ?? '—'}
        </div>
      )}

      {subtext && <div className="text-caption text-ink-secondary">{subtext}</div>}
    </div>
  );
}

export default StatTile;
