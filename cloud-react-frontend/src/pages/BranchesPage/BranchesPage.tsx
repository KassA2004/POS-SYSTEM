import { Plus, Store, SquarePen, Trash2, Ban, CircleCheck } from 'lucide-react';
import { AppShell } from '@/globalComponents/AppShell';
import { Button } from '@/globalComponents/Button';
import { DataTable, type Column } from '@/globalComponents/DataTable';
import { StatusBadge } from '@/globalComponents/StatusBadge';
import { EmptyState } from '@/globalComponents/EmptyState';
import { Alert } from '@/globalComponents/Alert';
import { ConfirmDialog } from '@/globalComponents/ConfirmDialog';
import { useBranches } from '@/hooks/useBranches';
import { formatDate } from '@/lib/format';
import type { Branch } from '@/types/domain';
import { BranchFormDrawer } from './components/BranchFormDrawer';

export function BranchesPage() {
  const branchesState = useBranches();
  const { branches, loading, error, openCreate, openEdit, setDeleteTarget, deleteTarget, deleting, confirmDelete } =
    branchesState;

  const columns: Column<Branch>[] = [
    {
      key: 'name',
      header: 'Branch',
      render: (row) => <span className="font-medium text-ink-primary">{row.name}</span>,
    },
    {
      key: 'address',
      header: 'Address',
      render: (row) => <span className="text-ink-secondary">{row.address}</span>,
    },
    {
      key: 'is_active',
      header: 'Status',
      render: (row) =>
        row.is_active ? (
          <StatusBadge variant="success" icon={<CircleCheck size={14} strokeWidth={2} />}>
            Active
          </StatusBadge>
        ) : (
          <StatusBadge variant="danger" icon={<Ban size={14} strokeWidth={2} />}>
            Inactive
          </StatusBadge>
        ),
    },
    {
      key: 'created_at',
      header: 'Created',
      render: (row) => <span className="text-body-sm text-ink-tertiary">{formatDate(row.created_at)}</span>,
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

  const showEmpty = !loading && !error && branches.length === 0;

  return (
    <AppShell
      title="Branches"
      actions={
        <Button variant="primary" icon={<Plus size={16} strokeWidth={1.5} />} onClick={openCreate}>
          New branch
        </Button>
      }
    >
      <div className="space-y-4">
        {error && <Alert variant="danger" title="Could not load branches">{error}</Alert>}

        {showEmpty ? (
          <div className="bg-surface border border-border-default rounded-lg">
            <EmptyState
              icon={<Store size={24} strokeWidth={1.5} />}
              title="No branches yet"
              message="Create your first branch to start assigning employees and tracking sales by location."
              action={
                <Button variant="primary" icon={<Plus size={16} strokeWidth={1.5} />} onClick={openCreate}>
                  New branch
                </Button>
              }
            />
          </div>
        ) : (
          <DataTable columns={columns} data={branches} loading={loading} emptyText="No branches found." />
        )}
      </div>

      <BranchFormDrawer state={branchesState} />

      <ConfirmDialog
        open={deleteTarget !== null}
        title={`Delete branch "${deleteTarget?.name ?? ''}"?`}
        message="This permanently deletes the branch and every employee assignment attached to it. Shifts and orders already recorded against this branch will block the delete."
        confirmLabel="Delete branch"
        loading={deleting}
        onConfirm={confirmDelete}
        onCancel={() => setDeleteTarget(null)}
      />
    </AppShell>
  );
}

export default BranchesPage;
