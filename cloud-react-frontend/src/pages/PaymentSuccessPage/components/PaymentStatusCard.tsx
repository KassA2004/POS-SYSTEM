import { Spinner } from '@/globalComponents/Spinner';
import { StatusBadge } from '@/globalComponents/StatusBadge';
import { Button } from '@/globalComponents/Button';
import { CircleCheck, CircleAlert, LogIn } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export interface PaymentStatusCardProps {
  status: 'verifying' | 'success' | 'error';
  errorMessage?: string | null;
  onRetry?: () => void;
}

export function PaymentStatusCard({ status, errorMessage, onRetry }: PaymentStatusCardProps) {
  const navigate = useNavigate();

  if (status === 'verifying') {
    return (
      <div className="flex flex-col items-center justify-center py-8 space-y-4 text-center">
        <Spinner size={32} />
        <div>
          <h2 className="text-h2 font-semibold text-ink-primary">Verifying Payment & Provisioning Schema</h2>
          <p className="text-body-sm text-ink-secondary mt-1">
            Please wait while Stripe webhook initializes your isolated tenant database.
          </p>
        </div>
      </div>
    );
  }

  if (status === 'error') {
    return (
      <div className="flex flex-col items-center justify-center py-6 space-y-4 text-center">
        <div className="w-12 h-12 rounded-full bg-danger-bg text-danger-fg flex items-center justify-center border border-danger-border">
          <CircleAlert size={24} strokeWidth={2} />
        </div>
        <div>
          <h2 className="text-h2 font-semibold text-ink-primary">Payment Verification Pending</h2>
          <p className="text-body-sm text-danger-fg mt-1">
            {errorMessage || 'Verification could not be confirmed immediately.'}
          </p>
        </div>
        <Button variant="secondary" onClick={onRetry} className="mt-2">
          Retry Verification
        </Button>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center py-6 space-y-4 text-center">
      <div className="w-12 h-12 rounded-full bg-success-bg text-success-fg flex items-center justify-center border border-success-border">
        <CircleCheck size={24} strokeWidth={2} />
      </div>
      <div>
        <StatusBadge variant="success" icon={<CircleCheck size={14} strokeWidth={2} />}>
          Tenant Active (State 1)
        </StatusBadge>
        <h2 className="text-h2 font-bold text-ink-primary mt-3">Payment Verified & Workspace Ready</h2>
        <p className="text-body-sm text-ink-secondary mt-1">
          Your tenant schema has been created successfully. You may now log in to your dashboard.
        </p>
      </div>
      <Button
        variant="primary"
        size="lg"
        icon={<LogIn size={18} strokeWidth={1.5} />}
        onClick={() => navigate('/login')}
        className="w-full mt-4 font-bold"
      >
        Go to Login
      </Button>
    </div>
  );
}

export default PaymentStatusCard;
