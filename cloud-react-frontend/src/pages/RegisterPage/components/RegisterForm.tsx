import { useRegisterForm } from '@/hooks/useRegisterForm';
import { FormField, Input, PasswordInput } from '@/globalComponents/Input';
import { Button } from '@/globalComponents/Button';
import { Zap } from 'lucide-react';

export function RegisterForm() {
  const {
    companyName,
    setCompanyName,
    email,
    setEmail,
    password,
    setPassword,
    confirmPassword,
    setConfirmPassword,
    loading,
    errorMessage,
    handleSubmit,
  } = useRegisterForm();

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {errorMessage && (
        <div className="p-3 text-caption text-danger-fg bg-danger-bg border border-danger-border rounded-md">
          {errorMessage}
        </div>
      )}

      <FormField label="Company / Business Name" required>
        <Input
          type="text"
          value={companyName}
          onChange={(e) => setCompanyName(e.target.value)}
          placeholder="Acme Coffee Shop"
          required
        />
      </FormField>

      <FormField label="Owner Email" required>
        <Input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="owner@acmecoffee.com"
          autoComplete="email"
          required
        />
      </FormField>

      <FormField label="Password" required hint="At least 8 characters long">
        <PasswordInput
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="••••••••"
          autoComplete="new-password"
          required
        />
      </FormField>

      <FormField label="Confirm Password" required>
        <PasswordInput
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          placeholder="••••••••"
          autoComplete="new-password"
          required
        />
      </FormField>

      <Button
        type="submit"
        variant="primary"
        size="lg"
        loading={loading}
        icon={<Zap size={18} strokeWidth={1.5} />}
        className="w-full font-bold mt-2"
      >
        Proceed to Stripe Checkout
      </Button>
    </form>
  );
}

export default RegisterForm;
