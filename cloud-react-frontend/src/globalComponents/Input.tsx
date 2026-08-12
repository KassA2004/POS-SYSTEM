import { useState, forwardRef, type InputHTMLAttributes, type ReactNode } from 'react';
import { Eye, EyeOff, Search, CircleAlert } from 'lucide-react';
import { cn } from '@/lib/cn';

export interface FormFieldProps {
  label?: string;
  required?: boolean;
  hint?: string;
  error?: string;
  children: ReactNode;
  className?: string;
}

export function FormField({ label, required, hint, error, children, className }: FormFieldProps) {
  return (
    <div className={cn('flex flex-col gap-1.5 w-full max-w-[480px]', className)}>
      {label && (
        <div className="flex items-center justify-between">
          <label className="text-caption font-medium text-ink-secondary">{label}</label>
          {required && <span className="text-caption text-ink-tertiary">Required</span>}
        </div>
      )}
      {children}
      {error ? (
        <div className="flex items-center gap-1 text-caption text-danger-fg" role="alert">
          <CircleAlert size={14} strokeWidth={2} />
          <span>{error}</span>
        </div>
      ) : hint ? (
        <p className="text-caption text-ink-tertiary">{hint}</p>
      ) : null}
    </div>
  );
}

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  invalid?: boolean;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(({ className, invalid, ...props }, ref) => {
  return (
    <input
      ref={ref}
      className={cn(
        'h-9 px-3 rounded-md bg-surface border border-border-control text-body text-ink-primary w-full ' +
          'placeholder:text-ink-tertiary transition-colors focus:border-border-control ' +
          'disabled:bg-surface-sunken disabled:opacity-50 disabled:cursor-not-allowed',
        invalid && 'border-danger-fg',
        className
      )}
      {...props}
    />
  );
});
Input.displayName = 'Input';

export type PasswordInputProps = Omit<InputProps, 'type'>;

export const PasswordInput = forwardRef<HTMLInputElement, PasswordInputProps>((props, ref) => {
  const [show, setShow] = useState(false);

  return (
    <div className="relative w-full">
      <Input ref={ref} type={show ? 'text' : 'password'} className="pr-10" {...props} />
      <button
        type="button"
        onClick={() => setShow(!show)}
        className="absolute right-2 top-1/2 -translate-y-1/2 text-ink-tertiary hover:text-ink-primary p-1 rounded cursor-pointer"
        aria-label={show ? 'Hide password' : 'Show password'}
      >
        {show ? <EyeOff size={16} strokeWidth={1.5} /> : <Eye size={16} strokeWidth={1.5} />}
      </button>
    </div>
  );
});
PasswordInput.displayName = 'PasswordInput';

export type SearchInputProps = InputProps;

export const SearchInput = forwardRef<HTMLInputElement, SearchInputProps>(({ className, ...props }, ref) => {
  return (
    <div className="relative w-full">
      <Search size={16} strokeWidth={1.5} className="absolute left-3 top-1/2 -translate-y-1/2 text-ink-tertiary" />
      <Input ref={ref} className={cn('pl-9', className)} {...props} />
    </div>
  );
});
SearchInput.displayName = 'SearchInput';
