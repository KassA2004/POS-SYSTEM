import { useEffect, useState, useRef, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { PaymentStatusCard } from './components/PaymentStatusCard';

export function PaymentSuccessPage() {
  const [searchParams] = useSearchParams();
  const sessionId = searchParams.get('session_id');
  const { verifyPayment } = useAuth();

  const [status, setStatus] = useState<'verifying' | 'success' | 'error'>('verifying');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const hasVerifiedRef = useRef(false);

  const handleVerify = useCallback(async () => {
    if (!sessionId) {
      setStatus('error');
      setErrorMessage('Missing Stripe session ID in URL parameters.');
      return;
    }

    setStatus('verifying');
    setErrorMessage(null);
    try {
      await verifyPayment(sessionId);
      setStatus('success');
    } catch (err: unknown) {
      setStatus('error');
      const msg = err instanceof Error ? err.message : 'Payment verification failed.';
      setErrorMessage(msg);
    }
  }, [sessionId, verifyPayment]);

  // Run verification once on mount (not as a synchronous setState inside effect)
  useEffect(() => {
    if (hasVerifiedRef.current) return;
    hasVerifiedRef.current = true;

    // Schedule the async work outside the synchronous effect body
    const controller = new AbortController();
    void handleVerify();
    return () => controller.abort();
  }, [handleVerify]);

  return (
    <div className="min-h-screen bg-canvas flex items-center justify-center p-4">
      <div className="w-full max-w-[440px] bg-surface border border-border-default rounded-2xl p-8 shadow-e2">
        <PaymentStatusCard status={status} errorMessage={errorMessage} onRetry={handleVerify} />
      </div>
    </div>
  );
}

export default PaymentSuccessPage;
