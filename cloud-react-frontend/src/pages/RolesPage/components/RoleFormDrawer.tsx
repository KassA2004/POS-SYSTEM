import { Drawer } from '@/globalComponents/Drawer';
import { Button } from '@/globalComponents/Button';
import { FormField, Input } from '@/globalComponents/Input';
import { Checkbox } from '@/globalComponents/Checkbox';
import { Alert } from '@/globalComponents/Alert';
import { permissionLabel } from '@/lib/format';
import type { useRoles } from '@/hooks/useRoles';

export interface RoleFormDrawerProps {
  state: ReturnType<typeof useRoles>;
}

export function RoleFormDrawer({ state }: RoleFormDrawerProps) {
  const {
    drawerOpen,
    editing,
    form,
    saving,
    formError,
    permissionGroups,
    closeDrawer,
    setName,
    togglePermission,
    toggleDomain,
    save,
  } = state;

  return (
    <Drawer
      open={drawerOpen}
      onClose={closeDrawer}
      width="md"
      title={editing ? 'Edit role' : 'New role'}
      description={
        editing ? `Updating "${editing.name}"` : 'Roles group permissions. Employees inherit them per branch.'
      }
      footer={
        <>
          <Button variant="secondary" onClick={closeDrawer} disabled={saving}>
            Cancel
          </Button>
          <Button variant="primary" onClick={save} loading={saving}>
            {editing ? 'Save changes' : 'Create role'}
          </Button>
        </>
      }
    >
      <div className="space-y-6">
        {formError && <Alert variant="danger">{formError}</Alert>}

        <FormField label="Role name" required hint="For example: Cashier, Shift Manager, Supervisor.">
          <Input value={form.name} onChange={(e) => setName(e.target.value)} placeholder="Shift Manager" autoFocus />
        </FormField>

        <div className="space-y-3">
          <div className="flex items-baseline justify-between">
            <span className="text-caption font-medium text-ink-secondary">Permissions</span>
            <span className="text-caption text-ink-tertiary">{form.permissionIds.length} selected</span>
          </div>

          {permissionGroups.length === 0 ? (
            <Alert variant="warning">No permission codes exist in this schema.</Alert>
          ) : (
            <div className="space-y-4">
              {permissionGroups.map(([domain, perms]) => {
                const allSelected = perms.every((p) => form.permissionIds.includes(p.id));
                return (
                  <div key={domain} className="border border-border-subtle rounded-lg overflow-hidden">
                    <div className="flex items-center justify-between bg-surface-sunken px-4 py-2 border-b border-border-subtle">
                      <span className="text-micro font-semibold uppercase tracking-[0.04em] text-ink-tertiary">
                        {domain}
                      </span>
                      <button
                        type="button"
                        onClick={() => toggleDomain(domain)}
                        className="text-caption font-medium text-ink-secondary hover:text-ink-primary cursor-pointer rounded"
                      >
                        {allSelected ? 'Clear all' : 'Select all'}
                      </button>
                    </div>
                    <div className="p-4 space-y-3">
                      {perms.map((permission) => (
                        <Checkbox
                          key={permission.id}
                          checked={form.permissionIds.includes(permission.id)}
                          onChange={() => togglePermission(permission.id)}
                          label={permissionLabel(permission.code)}
                          description={permission.description ?? permission.code}
                        />
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </Drawer>
  );
}

export default RoleFormDrawer;
