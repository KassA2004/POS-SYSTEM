import { forwardRef, type SelectHTMLAttributes } from 'react';
import { ChevronDown } from 'lucide-react';
import { cn } from '@/lib/cn';

export interface SelectOption {
  value: string | number;
  label: string;
}

export interface SelectProps extends Omit<SelectHTMLAttributes<HTMLSelectElement>, 'children'> {
  options: SelectOption[];
  placeholder?: string;
  invalid?: boolean;
}

/**
 * Native <select> styled to match Input. Native is deliberate: it gives correct
 * keyboard behaviour, mobile pickers and a11y for free.
 */
export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ className, options, placeholder, invalid, value, ...props }, ref) => {
    return (
      <div className="relative w-full">
        <select
          ref={ref}
          value={value}
          className={cn(
            'h-9 pl-3 pr-9 rounded-md bg-surface border border-border-control text-body text-ink-primary w-full ' +
              'appearance-none cursor-pointer transition-colors ' +
              'disabled:bg-surface-sunken disabled:opacity-50 disabled:cursor-not-allowed',
            value === '' && 'text-ink-tertiary',
            invalid && 'border-danger-fg',
            className
          )}
          {...props}
        >
          {placeholder && (
            <option value="" disabled>
              {placeholder}
            </option>
          )}
          {options.map((opt) => (
            <option key={opt.value} value={opt.value} className="text-ink-primary bg-surface">
              {opt.label}
            </option>
          ))}
        </select>
        <ChevronDown
          size={16}
          strokeWidth={1.5}
          aria-hidden="true"
          className="absolute right-3 top-1/2 -translate-y-1/2 text-ink-tertiary pointer-events-none"
        />
      </div>
    );
  }
);
Select.displayName = 'Select';

export default Select;
