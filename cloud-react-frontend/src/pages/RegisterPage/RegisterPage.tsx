import { Link } from 'react-router-dom';
import { Building2 } from 'lucide-react';
import { RegisterForm } from './components/RegisterForm';

export function RegisterPage() {
  return (
    <div className="min-h-screen bg-canvas flex items-center justify-center p-4">
      <div className="w-full max-w-[480px] bg-surface border border-border-default rounded-2xl p-8 shadow-e2 space-y-6">
        <div className="flex flex-col items-center text-center space-y-2">
          <div className="w-12 h-12 rounded-xl bg-ink-primary text-ink-inverse flex items-center justify-center shadow-e1">
            <Building2 size={24} strokeWidth={1.5} />
          </div>
          <h1 className="text-h1 font-bold text-ink-primary tracking-[-0.02em]">Get started with POS Cloud</h1>
          <p className="text-body-sm text-ink-secondary">
            Create a tenant workspace and complete checkout to activate your POS schema.
          </p>
        </div>

        <RegisterForm />

        <div className="text-center pt-2 border-t border-border-subtle">
          <p className="text-body-sm text-ink-secondary">
            Already have an active workspace?{' '}
            <Link to="/login" className="font-semibold text-ink-primary hover:underline">
              Sign in to your account
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}

export default RegisterPage;
