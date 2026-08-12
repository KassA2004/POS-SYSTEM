import { LoaderCircle } from 'lucide-react';
import { cn } from '@/lib/cn';

export interface SpinnerProps {
  size?: number;
  className?: string;
  label?: string;
}

export function Spinner({ size = 20, className, label = 'Loading...' }: SpinnerProps) {
  return (
    <div role="status" aria-label={label} className="inline-flex items-center justify-center">
      <LoaderCircle size={size} strokeWidth={1.5} className={cn('animate-spin text-ink-primary', className)} />
      <span className="sr-only">{label}</span>
    </div>
  );
}

export default Spinner;
