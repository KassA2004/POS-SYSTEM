import { forwardRef, type InputHTMLAttributes } from 'react';
import { Check } from 'lucide-react';
import { cn } from '@/lib/cn';

export interface CheckboxProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label?: string;
  description?: string;
}

export const Checkbox = forwardRef<HTMLInputElement, CheckboxProps>(
  ({ className, label, description, checked, disabled, ...props }, ref) => {
    return (
      <label
        className={cn(
          'flex items-start gap-2.5 cursor-pointer select-none group',
          disabled && 'opacity-50 cursor-not-allowed',
          className
        )}
      >
        <span className="relative flex items-center justify-center shrink-0 mt-0.5">
          <input
            ref={ref}
            type="checkbox"
            checked={checked}
            disabled={disabled}
            className="peer appearance-none w-4 h-4 rounded-xs border border-border-control bg-surface
                       checked:bg-ink-primary checked:border-ink-primary cursor-pointer
                       disabled:cursor-not-allowed transition-colors"
            {...props}
          />
          <Check
            size={12}
            strokeWidth={3}
            aria-hidden="true"
            className="absolute text-ink-inverse opacity-0 peer-checked:opacity-100 pointer-events-none"
          />
        </span>
        {(label || description) && (
          <span className="flex flex-col gap-0.5 leading-tight">
            {label && <span className="text-body text-ink-primary">{label}</span>}
            {description && <span className="text-caption text-ink-tertiary">{description}</span>}
          </span>
        )}
      </label>
    );
  }
);
Checkbox.displayName = 'Checkbox';

export default Checkbox;
