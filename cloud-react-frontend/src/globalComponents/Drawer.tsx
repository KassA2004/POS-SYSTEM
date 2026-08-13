import { useEffect, type ReactNode } from 'react';
import { X } from 'lucide-react';
import { cn } from '@/lib/cn';
import { Button } from './Button';

export interface DrawerProps {
  open: boolean;
  onClose: () => void;
  title: string;
  description?: string;
  children: ReactNode;
  footer?: ReactNode;
  width?: 'sm' | 'md';
}

/**
 * Right-side panel used for create/edit forms. Preferred over a modal for
 * anything with more than about three fields, because it keeps the table
 * the user was reading visible behind it.
 */
export function Drawer({ open, onClose, title, description, children, footer, width = 'sm' }: DrawerProps) {
  useEffect(() => {
    if (!open) return;

    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', onKeyDown);

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';

    return () => {
      document.removeEventListener('keydown', onKeyDown);
      document.body.style.overflow = previousOverflow;
    };
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      <div
        className="absolute inset-0 bg-black/50 animate-[fadeIn_120ms_ease-out]"
        onClick={onClose}
        aria-hidden="true"
      />
      <div
        role="dialog"
        aria-modal="true"
        aria-label={title}
        className={cn(
          'relative h-full bg-surface border-l border-border-default shadow-e3 flex flex-col w-full',
          width === 'sm' ? 'sm:w-[420px]' : 'sm:w-[560px]'
        )}
      >
        <header className="flex items-start justify-between gap-4 p-6 pb-4 border-b border-border-subtle">
          <div className="min-w-0">
            <h2 className="text-h3 font-semibold text-ink-primary">{title}</h2>
            {description && <p className="text-caption text-ink-tertiary mt-1">{description}</p>}
          </div>
          <Button variant="ghost" size="icon" onClick={onClose} aria-label="Close panel" className="shrink-0 -mt-1 -mr-2">
            <X size={18} strokeWidth={1.5} />
          </Button>
        </header>

        <div className="flex-1 overflow-y-auto p-6">{children}</div>

        {footer && (
          <footer className="p-6 pt-4 border-t border-border-subtle flex items-center justify-end gap-3">
            {footer}
          </footer>
        )}
      </div>
    </div>
  );
}

export default Drawer;
