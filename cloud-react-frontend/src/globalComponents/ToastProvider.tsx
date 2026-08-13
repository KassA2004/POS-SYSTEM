import { useCallback, useEffect, useRef, useState, type ReactNode } from 'react';
import { CircleCheck, CircleAlert, TriangleAlert, Info, X } from 'lucide-react';
import { ToastContext, type ToastMessage, type ToastVariant } from '@/context/ToastContextDef';
import { cn } from '@/lib/cn';

const styles: Record<ToastVariant, string> = {
  success: 'text-success-fg',
  warning: 'text-warning-fg',
  danger: 'text-danger-fg',
  info: 'text-info-fg',
};

const icons: Record<ToastVariant, typeof Info> = {
  success: CircleCheck,
  warning: TriangleAlert,
  danger: CircleAlert,
  info: Info,
};

/** Danger toasts never auto-dismiss - the user must acknowledge a failure. */
const DURATIONS: Record<ToastVariant, number> = {
  success: 5000,
  info: 5000,
  warning: 8000,
  danger: 0,
};

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<ToastMessage[]>([]);
  const nextId = useRef(1);
  const timers = useRef(new Map<number, ReturnType<typeof setTimeout>>());

  const dismiss = useCallback((id: number) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
    const timer = timers.current.get(id);
    if (timer) {
      clearTimeout(timer);
      timers.current.delete(id);
    }
  }, []);

  const toast = useCallback(
    (message: string, variant: ToastVariant = 'success') => {
      const id = nextId.current++;
      // Cap the stack at 3 so a burst of errors cannot cover the page.
      setToasts((prev) => [...prev.slice(-2), { id, variant, message }]);

      const duration = DURATIONS[variant];
      if (duration > 0) {
        timers.current.set(
          id,
          setTimeout(() => dismiss(id), duration)
        );
      }
    },
    [dismiss]
  );

  useEffect(() => {
    const pending = timers.current;
    return () => {
      pending.forEach(clearTimeout);
      pending.clear();
    };
  }, []);

  return (
    <ToastContext.Provider value={{ toast, dismiss }}>
      {children}
      <div
        aria-live="polite"
        className="fixed bottom-6 right-6 z-[70] flex flex-col gap-2 w-[360px] max-w-[calc(100vw-3rem)]"
      >
        {toasts.map((t) => {
          const Icon = icons[t.variant];
          return (
            <div
              key={t.id}
              role={t.variant === 'danger' ? 'alert' : 'status'}
              className="flex items-start gap-3 bg-surface-raised border border-border-default rounded-lg shadow-e3 p-4"
            >
              <Icon size={16} strokeWidth={1.5} aria-hidden="true" className={cn('shrink-0 mt-0.5', styles[t.variant])} />
              <p className="flex-1 text-body-sm text-ink-primary min-w-0 break-words">{t.message}</p>
              <button
                onClick={() => dismiss(t.id)}
                aria-label="Dismiss notification"
                className="shrink-0 text-ink-tertiary hover:text-ink-primary cursor-pointer rounded"
              >
                <X size={14} strokeWidth={2} />
              </button>
            </div>
          );
        })}
      </div>
    </ToastContext.Provider>
  );
}

export default ToastProvider;
