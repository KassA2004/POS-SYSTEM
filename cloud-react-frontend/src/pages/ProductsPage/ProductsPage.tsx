import { Plus, Package, SquarePen, Trash2, ChefHat, Ban, CircleCheck, TriangleAlert } from 'lucide-react';
import { AppShell } from '@/globalComponents/AppShell';
import { Button } from '@/globalComponents/Button';
import { DataTable, type Column } from '@/globalComponents/DataTable';
import { StatusBadge } from '@/globalComponents/StatusBadge';
import { EmptyState } from '@/globalComponents/EmptyState';
import { Alert } from '@/globalComponents/Alert';
import { ConfirmDialog } from '@/globalComponents/ConfirmDialog';
import { useProducts } from '@/hooks/useProducts';
import { formatMoney } from '@/lib/format';
import type { Product } from '@/types/domain';
import { ProductFormDrawer } from './components/ProductFormDrawer';
import { RecipeBuilderDrawer } from './components/RecipeBuilderDrawer';

export function ProductsPage() {
  const state = useProducts();
  const {
    products,
    ingredients,
    loading,
    error,
    openCreate,
    openEdit,
    openRecipe,
    deleteTarget,
    setDeleteTarget,
    deleting,
    confirmDelete,
  } = state;

  const ingredientNameById = new Map(ingredients.map((i) => [i.id, i.name]));

  const columns: Column<Product>[] = [
    {
      key: 'name',
      header: 'Product',
      render: (row) => <span className="font-medium text-ink-primary">{row.name}</span>,
    },
    {
      key: 'type',
      header: 'Source',
      render: (row) =>
        row.is_recipe ? (
          <StatusBadge variant="neutral" icon={<ChefHat size={14} strokeWidth={2} />}>
            Recipe
          </StatusBadge>
        ) : row.direct_warehouse_item_id ? (
          <span className="text-ink-secondary">
            {ingredientNameById.get(row.direct_warehouse_item_id) ?? `Item #${row.direct_warehouse_item_id}`}
          </span>
        ) : (
          <StatusBadge variant="warning" icon={<TriangleAlert size={14} strokeWidth={2} />}>
            Unlinked
          </StatusBadge>
        ),
    },
    {
      key: 'price',
      header: 'Price',
      align: 'right',
      render: (row) => (
        <span className="tabular-nums text-ink-primary">
          <span className="text-ink-tertiary mr-0.5">$</span>
          {formatMoney(row.price)}
        </span>
      ),
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
      key: 'actions',
      header: '',
      align: 'right',
      render: (row) => (
        <div className="flex items-center justify-end gap-1">
          {row.is_recipe && (
            <Button variant="ghost" size="sm" onClick={() => openRecipe(row)} aria-label={`Edit recipe for ${row.name}`}>
              <ChefHat size={16} strokeWidth={1.5} />
            </Button>
          )}
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

  const showEmpty = !loading && !error && products.length === 0;
  const noIngredients = ingredients.length === 0;

  return (
    <AppShell
      title="Products"
      actions={
        <Button
          variant="primary"
          icon={<Plus size={16} strokeWidth={1.5} />}
          onClick={openCreate}
          disabled={noIngredients}
        >
          New product
        </Button>
      }
    >
      <div className="space-y-4">
        {error && <Alert variant="danger" title="Could not load products">{error}</Alert>}

        {noIngredients && (
          <Alert variant="info" title="Add ingredients first">
            Every product draws stock from the warehouse — either mapped directly to a single ingredient, or through a
            recipe of several. Create at least one ingredient before adding products.
          </Alert>
        )}

        {showEmpty && !noIngredients ? (
          <div className="bg-surface border border-border-default rounded-lg">
            <EmptyState
              icon={<Package size={24} strokeWidth={1.5} />}
              title="No products yet"
              message="Products are what customers buy. Map one directly to an ingredient, or build it from a recipe."
              action={
                <Button variant="primary" icon={<Plus size={16} strokeWidth={1.5} />} onClick={openCreate}>
                  New product
                </Button>
              }
            />
          </div>
        ) : (
          !showEmpty && <DataTable columns={columns} data={products} loading={loading} emptyText="No products found." />
        )}
      </div>

      <ProductFormDrawer state={state} />
      <RecipeBuilderDrawer state={state} />

      <ConfirmDialog
        open={deleteTarget !== null}
        title={`Delete product "${deleteTarget?.name ?? ''}"?`}
        message="This also deletes its recipe lines. Products that already appear on recorded orders cannot be deleted — deactivate them instead."
        confirmLabel="Delete product"
        loading={deleting}
        onConfirm={confirmDelete}
        onCancel={() => setDeleteTarget(null)}
      />
    </AppShell>
  );
}

export default ProductsPage;
