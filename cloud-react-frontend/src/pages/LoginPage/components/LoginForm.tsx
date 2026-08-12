import { useLoginForm } from '@/hooks/useLoginForm';
import { FormField, Input, PasswordInput } from '@/globalComponents/Input';
import { Button } from '@/globalComponents/Button';
import { LogIn } from 'lucide-react';

export function LoginForm() {
  const { email, setEmail, password, setPassword, loading, errorMessage, handleSubmit } = useLoginForm();

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {errorMessage && (
        <div className="p-3 text-caption text-danger-fg bg-danger-bg border border-danger-border rounded-md">
          {errorMessage}
        </div>
      )}

      <FormField label="Email address" required>
        <Input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="owner@company.com"
          autoComplete="email"
          required
        />
      </FormField>

      <FormField label="Password" required>
        <PasswordInput
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="••••••••"
          autoComplete="current-password"
          required
        />
      </FormField>

      <Button
        type="submit"
        variant="primary"
        size="lg"
        loading={loading}
        icon={<LogIn size={18} strokeWidth={1.5} />}
        className="w-full font-bold mt-2"
      >
        Sign in to Cloud POS
      </Button>
    </form>
  );
}

export default LoginForm;
