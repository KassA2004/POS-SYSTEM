import { Drawer } from '@/globalComponents/Drawer';
import { Button } from '@/globalComponents/Button';
import { FormField, Input } from '@/globalComponents/Input';
import { Checkbox } from '@/globalComponents/Checkbox';
import { Alert } from '@/globalComponents/Alert';
import type { useBranches } from '@/hooks/useBranches';

export interface BranchFormDrawerProps {
  state: ReturnType<typeof useBranches>;
}

export function BranchFormDrawer({ state }: BranchFormDrawerProps) {
  const { drawerOpen, editing, form, saving, formError, closeDrawer, updateForm, save } = state;

  return (
    <Drawer
      open={drawerOpen}
      onClose={closeDrawer}
      title={editing ? 'Edit branch' : 'New branch'}
      description={editing ? `Updating "${editing.name}"` : 'Add a physical location to this workspace.'}
      footer={
        <>
          <Button variant="secondary" onClick={closeDrawer} disabled={saving}>
            Cancel
          </Button>
          <Button variant="primary" onClick={save} loading={saving}>
            {editing ? 'Save changes' : 'Create branch'}
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

        <FormField label="Branch name" required>
          <Input
            value={form.name}
            onChange={(e) => updateForm({ name: e.target.value })}
            placeholder="Downtown Coffee"
            autoFocus
          />
        </FormField>

        <FormField label="Address" required>
          <Input
            value={form.address}
            onChange={(e) => updateForm({ address: e.target.value })}
            placeholder="12 Market Street, Springfield"
          />
        </FormField>

        <Checkbox
          checked={form.is_active}
          onChange={(e) => updateForm({ is_active: e.target.checked })}
          label="Active"
          description="Inactive branches stay in reports but cannot open new shifts."
        />

        {/* Enables Enter-to-submit without rendering a second visible button. */}
        <button type="submit" className="hidden" aria-hidden="true" tabIndex={-1} />
      </form>
    </Drawer>
  );
}

export default BranchFormDrawer;
