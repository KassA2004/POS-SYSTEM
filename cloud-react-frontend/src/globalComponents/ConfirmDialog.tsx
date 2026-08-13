import { useEffect, useRef } from 'react';
import { TriangleAlert } from 'lucide-react';
import { Button } from './Button';

export interface ConfirmDialogProps {
  open: boolean;
  title: string;
  /** State the consequence in plain language, including any cascade effects. */
  message: string;
  /** Verb-first, e.g. "Delete branch" - never "OK". */
  confirmLabel?: string;
  loading?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

/**
 * Required in front of every DELETE call. Cancel takes initial focus so that
 * a stray Enter keypress can never destroy data.
 */
export function ConfirmDialog({
  open,
  title,
  message,
  confirmLabel = 'Delete',
  loading,
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  const cancelRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!open) return;
    cancelRef.current?.focus();

    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onCancel();
    };
    document.addEventListener('keydown', onKeyDown);
    return () => document.removeEventListener('keydown', onKeyDown);
  }, [open, onCancel]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/50" onClick={onCancel} aria-hidden="true" />
      <div
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="confirm-title"
        className="relative w-full max-w-[400px] bg-surface-raised border border-border-default rounded-xl shadow-e3 p-6"
      >
        <div className="flex gap-3">
          <div className="w-9 h-9 shrink-0 rounded-full bg-danger-bg text-danger-fg border border-danger-border flex items-center justify-center">
            <TriangleAlert size={18} strokeWidth={2} aria-hidden="true" />
          </div>
          <div className="min-w-0">
            <h2 id="confirm-title" className="text-h3 font-semibold text-ink-primary">
              {title}
            </h2>
            <p className="text-body-sm text-ink-secondary mt-1.5">{message}</p>
          </div>
        </div>

        <div className="flex items-center justify-end gap-3 mt-6">
          <Button ref={cancelRef} variant="secondary" onClick={onCancel} disabled={loading}>
            Cancel
          </Button>
          <Button variant="danger" onClick={onConfirm} loading={loading}>
            {confirmLabel}
          </Button>
        </div>
      </div>
    </div>
  );
}

export default ConfirmDialog;
