import { Plus, Boxes, SquarePen, Trash2, TriangleAlert, Warehouse } from 'lucide-react';
import { AppShell } from '@/globalComponents/AppShell';
import { Button } from '@/globalComponents/Button';
import { DataTable, type Column } from '@/globalComponents/DataTable';
import { StatusBadge } from '@/globalComponents/StatusBadge';
import { EmptyState } from '@/globalComponents/EmptyState';
import { Alert } from '@/globalComponents/Alert';
import { ConfirmDialog } from '@/globalComponents/ConfirmDialog';
import { useIngredients, type IngredientRow } from '@/hooks/useIngredients';
import { formatQuantity } from '@/lib/format';
import { IngredientFormDrawer } from './components/IngredientFormDrawer';
import { StockAdjustDrawer } from './components/StockAdjustDrawer';

export function IngredientsPage() {
  const state = useIngredients();
  const {
    rows,
    lowStockCount,
    loading,
    error,
    openCreate,
    openEdit,
    openStock,
    deleteTarget,
    setDeleteTarget,
    deleting,
    confirmDelete,
  } = state;

  const columns: Column<IngredientRow>[] = [
    {
      key: 'name',
      header: 'Ingredient',
      render: (row) => <span className="font-medium text-ink-primary">{row.name}</span>,
    },
    {
      key: 'sku',
      header: 'SKU',
      render: (row) =>
        row.sku ? (
          <span className="font-mono text-body-sm text-ink-secondary">{row.sku}</span>
        ) : (
          <span className="text-ink-tertiary">—</span>
        ),
    },
    {
      key: 'current_stock',
      header: 'In stock',
      align: 'right',
      render: (row) => (
        <div className="flex items-center justify-end gap-2">
          {row.is_low_stock && (
            <StatusBadge variant="warning" icon={<TriangleAlert size={14} strokeWidth={2} />}>
              Low
            </StatusBadge>
          )}
          <span className="tabular-nums text-ink-primary">{formatQuantity(row.current_stock)}</span>
          <span className="text-caption text-ink-tertiary w-10 text-left">{row.unit_of_measure}</span>
        </div>
      ),
    },
    {
      key: 'minimum_stock',
      header: 'Minimum',
      align: 'right',
      render: (row) => (
        <span className="tabular-nums text-ink-secondary">{formatQuantity(row.minimum_stock)}</span>
      ),
    },
    {
      key: 'actions',
      header: '',
      align: 'right',
      render: (row) => (
        <div className="flex items-center justify-end gap-1">
          <Button variant="ghost" size="sm" onClick={() => openStock(row)} aria-label={`Adjust stock for ${row.name}`}>
            <Warehouse size={16} strokeWidth={1.5} />
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

  const showEmpty = !loading && !error && rows.length === 0;

  return (
    <AppShell
      title="Ingredients"
      actions={
        <Button variant="primary" icon={<Plus size={16} strokeWidth={1.5} />} onClick={openCreate}>
          New ingredient
        </Button>
      }
    >
      <div className="space-y-4">
        {error && <Alert variant="danger" title="Could not load ingredients">{error}</Alert>}

        {lowStockCount > 0 && (
          <Alert variant="warning" title={`${lowStockCount} ingredient${lowStockCount === 1 ? '' : 's'} at or below minimum stock`}>
            Restock these before they block recipe-based sales — an order fails entirely if any ingredient is short.
          </Alert>
        )}

        {showEmpty ? (
          <div className="bg-surface border border-border-default rounded-lg">
            <EmptyState
              icon={<Boxes size={24} strokeWidth={1.5} />}
              title="No ingredients yet"
              message="Ingredients are the raw materials held in your central warehouse. Products either map to one directly, or combine several through a recipe."
              action={
                <Button variant="primary" icon={<Plus size={16} strokeWidth={1.5} />} onClick={openCreate}>
                  New ingredient
                </Button>
              }
            />
          </div>
        ) : (
          <DataTable columns={columns} data={rows} loading={loading} emptyText="No ingredients found." />
        )}
      </div>

      <IngredientFormDrawer state={state} />
      <StockAdjustDrawer state={state} />

      <ConfirmDialog
        open={deleteTarget !== null}
        title={`Delete ingredient "${deleteTarget?.name ?? ''}"?`}
        message="This also removes its warehouse stock record. Any product recipe that uses this ingredient will lose that line, and products mapped to it directly will be unlinked."
        confirmLabel="Delete ingredient"
        loading={deleting}
        onConfirm={confirmDelete}
        onCancel={() => setDeleteTarget(null)}
      />
    </AppShell>
  );
}

export default IngredientsPage;
