import { Link } from 'react-router-dom';
import { Zap } from 'lucide-react';
import { LoginForm } from './components/LoginForm';

export function LoginPage() {
  return (
    <div className="min-h-screen bg-canvas flex items-center justify-center p-4">
      <div className="w-full max-w-[420px] bg-surface border border-border-default rounded-2xl p-8 shadow-e2 space-y-6">
        <div className="flex flex-col items-center text-center space-y-2">
          <div className="w-12 h-12 rounded-xl bg-ink-primary text-ink-inverse flex items-center justify-center shadow-e1">
            <Zap size={24} strokeWidth={2} />
          </div>
          <h1 className="text-h1 font-bold text-ink-primary tracking-[-0.02em]">Welcome back</h1>
          <p className="text-body-sm text-ink-secondary">Sign in to manage your POS Cloud workspace</p>
        </div>

        <LoginForm />

        <div className="text-center pt-2 border-t border-border-subtle">
          <p className="text-body-sm text-ink-secondary">
            Don&apos;t have a workspace?{' '}
            <Link to="/register" className="font-semibold text-ink-primary hover:underline">
              Create a tenant workspace
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;
