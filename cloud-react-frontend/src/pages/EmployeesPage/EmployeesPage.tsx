import { Plus, Users, SquarePen, Trash2, UserPlus, TriangleAlert } from 'lucide-react';
import { AppShell } from '@/globalComponents/AppShell';
import { Button } from '@/globalComponents/Button';
import { DataTable, type Column } from '@/globalComponents/DataTable';
import { StatusBadge } from '@/globalComponents/StatusBadge';
import { EmptyState } from '@/globalComponents/EmptyState';
import { Alert } from '@/globalComponents/Alert';
import { ConfirmDialog } from '@/globalComponents/ConfirmDialog';
import { useEmployees } from '@/hooks/useEmployees';
import { formatDate } from '@/lib/format';
import type { Employee } from '@/types/domain';
import { EmployeeFormDrawer } from './components/EmployeeFormDrawer';
import { EmployeeAssignmentDrawer } from './components/EmployeeAssignmentDrawer';

export function EmployeesPage() {
  const state = useEmployees();
  const {
    employees,
    assignmentsByEmployee,
    roles,
    loading,
    error,
    openCreate,
    openEdit,
    openAssign,
    deleteTarget,
    setDeleteTarget,
    deleting,
    confirmDelete,
  } = state;

  const columns: Column<Employee>[] = [
    {
      key: 'name',
      header: 'Employee',
      render: (row) => (
        <div className="flex flex-col">
          <span className="font-medium text-ink-primary">{row.name}</span>
          {row.phone && <span className="text-caption text-ink-tertiary">{row.phone}</span>}
        </div>
      ),
    },
    {
      key: 'assignments',
      header: 'Branches & roles',
      render: (row) => {
        const list = assignmentsByEmployee.get(row.id) ?? [];
        if (list.length === 0) {
          return <span className="text-ink-tertiary">Unassigned</span>;
        }
        return (
          <div className="flex flex-wrap gap-1.5">
            {list.map((a) => (
              <StatusBadge
                key={a.id}
                variant={a.role_name ? 'neutral' : 'warning'}
                icon={a.role_name ? undefined : <TriangleAlert size={14} strokeWidth={2} />}
              >
                {a.branch_name}
                {a.role_name ? ` · ${a.role_name}` : ' · no role'}
              </StatusBadge>
            ))}
          </div>
        );
      },
    },
    {
      key: 'date_of_birth',
      header: 'Date of birth',
      render: (row) => <span className="text-body-sm text-ink-tertiary">{formatDate(row.date_of_birth)}</span>,
    },
    {
      key: 'actions',
      header: '',
      align: 'right',
      render: (row) => (
        <div className="flex items-center justify-end gap-1">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => openAssign(row)}
            aria-label={`Manage branch assignments for ${row.name}`}
          >
            <UserPlus size={16} strokeWidth={1.5} />
          </Button>
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

  const showEmpty = !loading && !error && employees.length === 0;

  return (
    <AppShell
      title="Employees"
      actions={
        <Button variant="primary" icon={<Plus size={16} strokeWidth={1.5} />} onClick={openCreate}>
          New employee
        </Button>
      }
    >
      <div className="space-y-4">
        {error && <Alert variant="danger" title="Could not load employees">{error}</Alert>}

        {roles.length === 0 && employees.length > 0 && (
          <Alert variant="info" title="No roles defined yet">
            Employees can be assigned to a branch without a role, but they will not be able to sign in at the POS
            terminal until a role grants them permissions. Create a role first.
          </Alert>
        )}

        {showEmpty ? (
          <div className="bg-surface border border-border-default rounded-lg">
            <EmptyState
              icon={<Users size={24} strokeWidth={1.5} />}
              title="No employees yet"
              message="Add your staff, then assign each person to a branch with the role they hold there."
              action={
                <Button variant="primary" icon={<Plus size={16} strokeWidth={1.5} />} onClick={openCreate}>
                  New employee
                </Button>
              }
            />
          </div>
        ) : (
          <DataTable columns={columns} data={employees} loading={loading} emptyText="No employees found." />
        )}
      </div>

      <EmployeeFormDrawer state={state} />
      <EmployeeAssignmentDrawer state={state} />

      <ConfirmDialog
        open={deleteTarget !== null}
        title={`Delete employee "${deleteTarget?.name ?? ''}"?`}
        message="This permanently deletes the employee and all of their branch assignments. Shifts, orders or cash transactions already recorded against them will block the delete."
        confirmLabel="Delete employee"
        loading={deleting}
        onConfirm={confirmDelete}
        onCancel={() => setDeleteTarget(null)}
      />
    </AppShell>
  );
}

export default EmployeesPage;
