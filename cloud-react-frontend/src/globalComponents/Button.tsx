import { forwardRef } from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { LoaderCircle } from 'lucide-react';
import { cn } from '@/lib/cn';
import type { ButtonHTMLAttributes, ReactNode } from 'react';

const buttonVariants = cva(
  'inline-flex items-center justify-center gap-2 rounded-md font-medium whitespace-nowrap ' +
    'transition-[background-color,border-color,transform,opacity] duration-[120ms] ease-standard ' +
    'active:scale-[0.98] disabled:pointer-events-none disabled:opacity-50 cursor-pointer',
  {
    variants: {
      variant: {
        primary:   'bg-ink-primary text-ink-inverse hover:opacity-90',
        secondary: 'bg-surface text-ink-primary border border-border-control hover:bg-surface-hover',
        ghost:     'bg-transparent text-ink-secondary hover:bg-surface-hover hover:text-ink-primary',
        danger:    'bg-danger-fg text-white hover:opacity-90',
        link:      'bg-transparent text-ink-primary underline underline-offset-4 hover:opacity-70',
      },
      size: {
        sm:   'h-8 px-3 text-body-sm',
        md:   'h-9 px-4 text-body',
        lg:   'h-11 px-6 text-lead',
        icon: 'h-9 w-9 p-0 aspect-square',
      },
    },
    defaultVariants: { variant: 'secondary', size: 'md' },
  }
);

export type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> &
  VariantProps<typeof buttonVariants> & { loading?: boolean; icon?: ReactNode };

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, loading, icon, children, disabled, type = 'button', ...rest }, ref) => {
    return (
      <button
        ref={ref}
        type={type}
        className={cn(buttonVariants({ variant, size }), className)}
        disabled={disabled || loading}
        aria-busy={loading || undefined}
        {...rest}
      >
        {loading ? <LoaderCircle size={16} strokeWidth={1.5} className="animate-spin" aria-hidden="true" /> : icon}
        {children}
      </button>
    );
  }
);
Button.displayName = 'Button';

export default Button;
