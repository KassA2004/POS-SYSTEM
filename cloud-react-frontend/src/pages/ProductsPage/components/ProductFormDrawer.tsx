import { Drawer } from '@/globalComponents/Drawer';
import { Button } from '@/globalComponents/Button';
import { FormField, Input } from '@/globalComponents/Input';
import { Select } from '@/globalComponents/Select';
import { Checkbox } from '@/globalComponents/Checkbox';
import { Alert } from '@/globalComponents/Alert';
import type { useProducts } from '@/hooks/useProducts';

export interface ProductFormDrawerProps {
  state: ReturnType<typeof useProducts>;
}

export function ProductFormDrawer({ state }: ProductFormDrawerProps) {
  const { drawerOpen, editing, form, saving, formError, ingredients, closeDrawer, updateForm, save } = state;

  return (
    <Drawer
      open={drawerOpen}
      onClose={closeDrawer}
      title={editing ? 'Edit product' : 'New product'}
      description={editing ? `Updating "${editing.name}"` : 'Something a customer can buy at the register.'}
      footer={
        <>
          <Button variant="secondary" onClick={closeDrawer} disabled={saving}>
            Cancel
          </Button>
          <Button variant="primary" onClick={save} loading={saving}>
            {editing ? 'Save changes' : 'Create product'}
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

        <FormField label="Product name" required>
          <Input
            value={form.name}
            onChange={(e) => updateForm({ name: e.target.value })}
            placeholder="Flat White"
            autoFocus
          />
        </FormField>

        <FormField label="Price" required>
          <Input
            type="number"
            min="0"
            step="0.01"
            value={form.price}
            onChange={(e) => updateForm({ price: e.target.value })}
            className="text-right tabular-nums"
          />
        </FormField>

        <div className="space-y-3 border-t border-border-subtle pt-5">
          <span className="text-caption font-medium text-ink-secondary">Stock source</span>

          <Checkbox
            checked={form.is_recipe}
            onChange={(e) => updateForm({ is_recipe: e.target.checked })}
            label="Built from a recipe"
            description="Selling it deducts several ingredients at once. Leave off for a product that maps to a single stocked item."
          />

          {form.is_recipe ? (
            <p className="text-caption text-ink-tertiary pl-6">
              {editing
                ? 'Manage the ingredient lines from the recipe action on the table.'
                : 'You will be taken to the recipe builder after creating this product.'}
            </p>
          ) : (
            <FormField label="Draws stock from" required hint="The single warehouse item one sale deducts.">
              <Select
                value={form.direct_warehouse_item_id}
                onChange={(e) => updateForm({ direct_warehouse_item_id: e.target.value })}
                placeholder="Choose an ingredient"
                options={ingredients.map((i) => ({
                  value: i.id,
                  label: `${i.name} (${i.unit_of_measure})`,
                }))}
              />
            </FormField>
          )}
        </div>

        <div className="border-t border-border-subtle pt-5">
          <Checkbox
            checked={form.is_active}
            onChange={(e) => updateForm({ is_active: e.target.checked })}
            label="Active"
            description="Inactive products stay in past orders and reports but cannot be sold."
          />
        </div>

        <button type="submit" className="hidden" aria-hidden="true" tabIndex={-1} />
      </form>
    </Drawer>
  );
}

export default ProductFormDrawer;
