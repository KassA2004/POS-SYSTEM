import { Plus, ShieldCheck, SquarePen, Trash2 } from 'lucide-react';
import { AppShell } from '@/globalComponents/AppShell';
import { Button } from '@/globalComponents/Button';
import { DataTable, type Column } from '@/globalComponents/DataTable';
import { StatusBadge } from '@/globalComponents/StatusBadge';
import { EmptyState } from '@/globalComponents/EmptyState';
import { Alert } from '@/globalComponents/Alert';
import { ConfirmDialog } from '@/globalComponents/ConfirmDialog';
import { useRoles } from '@/hooks/useRoles';
import type { Role } from '@/types/domain';
import { RoleFormDrawer } from './components/RoleFormDrawer';

export function RolesPage() {
  const rolesState = useRoles();
  const {
    roles,
    permissions,
    loading,
    permissionsLoading,
    error,
    openCreate,
    openEdit,
    deleteTarget,
    setDeleteTarget,
    deleting,
    confirmDelete,
  } = rolesState;

  const columns: Column<Role>[] = [
    {
      key: 'name',
      header: 'Role',
      render: (row) => <span className="font-medium text-ink-primary">{row.name}</span>,
    },
    {
      key: 'permissions',
      header: 'Permissions',
      render: (row) => (
        <div className="flex flex-wrap gap-1.5">
          {row.permissions.length === 0 ? (
            <span className="text-ink-tertiary">None</span>
          ) : (
            row.permissions.map((p) => (
              <span
                key={p.id}
                className="font-mono text-caption text-ink-secondary bg-surface-sunken border border-border-subtle rounded-sm px-1.5 py-0.5"
              >
                {p.code}
              </span>
            ))
          )}
        </div>
      ),
    },
    {
      key: 'count',
      header: 'Granted',
      align: 'right',
      render: (row) => <StatusBadge variant="neutral">{row.permissions.length}</StatusBadge>,
    },
    {
      key: 'actions',
      header: '',
      align: 'right',
      render: (row) => (
        <div className="flex items-center justify-end gap-1">
          <Button variant="ghost" size="sm" onClick={() => openEdit(row)} aria-label={`Edit ${row.name}`}>
            <SquarePen size={16} strokeWidth={1.5} />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setDeleteTarget(row)}
            aria-label={`Delete ${row.name}`}
            className="hover:text-danger-fg hover:bg-danger-bg"
          >
            <Trash2 size={16} strokeWidth={1.5} />
          </Button>
        </div>
      ),
    },
  ];

  const noPermissionCatalogue = !permissionsLoading && permissions.length === 0;
  const showEmpty = !loading && !error && roles.length === 0;

  return (
    <AppShell
      title="Roles & Permissions"
      actions={
        <Button
          variant="primary"
          icon={<Plus size={16} strokeWidth={1.5} />}
          onClick={openCreate}
          disabled={noPermissionCatalogue}
        >
          New role
        </Button>
      }
    >
      <div className="space-y-4">
        {error && <Alert variant="danger" title="Could not load roles">{error}</Alert>}

        {noPermissionCatalogue && (
          <Alert variant="warning" title="Permission catalogue is empty">
            This tenant schema was provisioned before permission codes were seeded, so no role can be created — the API
            requires at least one permission per role. Re-provision the tenant, or insert the codes from{' '}
            <span className="font-mono">tenant_schema.sql</span> into this schema&apos;s{' '}
            <span className="font-mono">permissions</span> table.
          </Alert>
        )}

        {showEmpty && !noPermissionCatalogue ? (
          <div className="bg-surface border border-border-default rounded-lg">
            <EmptyState
              icon={<ShieldCheck size={24} strokeWidth={1.5} />}
              title="No roles yet"
              message="Roles are containers for permissions. Create one, then assign it to employees per branch."
              action={
                <Button variant="primary" icon={<Plus size={16} strokeWidth={1.5} />} onClick={openCreate}>
                  New role
                </Button>
              }
            />
          </div>
        ) : (
          !showEmpty && <DataTable columns={columns} data={roles} loading={loading} emptyText="No roles found." />
        )}
      </div>

      <RoleFormDrawer state={rolesState} />

      <ConfirmDialog
        open={deleteTarget !== null}
        title={`Delete role "${deleteTarget?.name ?? ''}"?`}
        message="Employees currently holding this role at any branch will block the delete. Remove those assignments first."
        confirmLabel="Delete role"
        loading={deleting}
        onConfirm={confirmDelete}
        onCancel={() => setDeleteTarget(null)}
      />
    </AppShell>
  );
}

export default RolesPage;
