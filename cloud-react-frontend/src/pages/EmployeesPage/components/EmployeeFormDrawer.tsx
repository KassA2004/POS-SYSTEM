import { Drawer } from '@/globalComponents/Drawer';
import { Button } from '@/globalComponents/Button';
import { FormField, Input } from '@/globalComponents/Input';
import { Alert } from '@/globalComponents/Alert';
import type { useEmployees } from '@/hooks/useEmployees';

export interface EmployeeFormDrawerProps {
  state: ReturnType<typeof useEmployees>;
}

export function EmployeeFormDrawer({ state }: EmployeeFormDrawerProps) {
  const { drawerOpen, editing, form, saving, formError, closeDrawer, updateForm, save } = state;

  return (
    <Drawer
      open={drawerOpen}
      onClose={closeDrawer}
      title={editing ? 'Edit employee' : 'New employee'}
      description={editing ? `Updating "${editing.name}"` : 'Staff who will operate the POS terminal.'}
      footer={
        <>
          <Button variant="secondary" onClick={closeDrawer} disabled={saving}>
            Cancel
          </Button>
          <Button variant="primary" onClick={save} loading={saving}>
            {editing ? 'Save changes' : 'Create employee'}
          </Button>
        </>
      }
    >
      <form
        className="space-y-5"
        onSubmit={(e) => {
          e.preventDefault();
          void save();
        }}
      >
        {formError && <Alert variant="danger">{formError}</Alert>}

        <FormField label="Full name" required>
          <Input
            value={form.name}
            onChange={(e) => updateForm({ name: e.target.value })}
            placeholder="Jordan Ellis"
            autoFocus
          />
        </FormField>

        <FormField label="Phone">
          <Input
            value={form.phone}
            onChange={(e) => updateForm({ phone: e.target.value })}
            placeholder="+1 555 0134"
          />
        </FormField>

        <FormField label="Date of birth">
          <Input
            type="date"
            value={form.date_of_birth}
            onChange={(e) => updateForm({ date_of_birth: e.target.value })}
          />
        </FormField>

        <FormField
          label="POS terminal PIN"
          hint={
            editing
              ? 'Leave blank to keep the current PIN. 4 to 8 digits.'
              : 'Optional. 4 to 8 digits, used to sign in at the register.'
          }
        >
          <Input
            value={form.pin}
            onChange={(e) => updateForm({ pin: e.target.value.replace(/\D/g, '').slice(0, 8) })}
            placeholder="••••"
            inputMode="numeric"
            autoComplete="off"
          />
        </FormField>

        {/* The API never returns a PIN, so an admin cannot verify one is set by
            looking at the row. Say so rather than implying the field is empty. */}
        {editing && (
          <p className="text-caption text-ink-tertiary">
            Existing PINs are write-only and cannot be displayed. Entering a value here replaces it.
          </p>
        )}

        <button type="submit" className="hidden" aria-hidden="true" tabIndex={-1} />
      </form>
    </Drawer>
  );
}

export default EmployeeFormDrawer;
