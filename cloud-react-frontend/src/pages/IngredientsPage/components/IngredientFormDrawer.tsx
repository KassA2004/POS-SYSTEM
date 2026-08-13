import { Drawer } from '@/globalComponents/Drawer';
import { Button } from '@/globalComponents/Button';
import { FormField, Input } from '@/globalComponents/Input';
import { Alert } from '@/globalComponents/Alert';
import type { useIngredients } from '@/hooks/useIngredients';

export interface IngredientFormDrawerProps {
  state: ReturnType<typeof useIngredients>;
}

export function IngredientFormDrawer({ state }: IngredientFormDrawerProps) {
  const { drawerOpen, editing, form, saving, formError, closeDrawer, updateForm, save } = state;

  return (
    <Drawer
      open={drawerOpen}
      onClose={closeDrawer}
      title={editing ? 'Edit ingredient' : 'New ingredient'}
      description={
        editing ? `Updating "${editing.name}"` : 'A raw material held in the shared central warehouse.'
      }
      footer={
        <>
          <Button variant="secondary" onClick={closeDrawer} disabled={saving}>
            Cancel
          </Button>
          <Button variant="primary" onClick={save} loading={saving}>
            {editing ? 'Save changes' : 'Create ingredient'}
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

        <FormField label="Name" required>
          <Input
            value={form.name}
            onChange={(e) => updateForm({ name: e.target.value })}
            placeholder="Espresso Beans"
            autoFocus
          />
        </FormField>

        <FormField label="SKU" hint="Optional, but must be unique across all ingredients.">
          <Input
            value={form.sku}
            onChange={(e) => updateForm({ sku: e.target.value })}
            placeholder="ESP-BEAN-1KG"
            className="font-mono"
          />
        </FormField>

        <FormField label="Unit of measure" required hint="How stock is counted: kg, L, pcs, g.">
          <Input
            value={form.unit_of_measure}
            onChange={(e) => updateForm({ unit_of_measure: e.target.value })}
            placeholder="kg"
          />
        </FormField>

        <FormField label="Minimum stock" hint="Anything at or below this level is flagged as low stock.">
          <Input
            type="number"
            min="0"
            step="0.001"
            value={form.minimum_stock}
            onChange={(e) => updateForm({ minimum_stock: e.target.value })}
            className="text-right tabular-nums"
          />
        </FormField>

        {!editing && (
          <p className="text-caption text-ink-tertiary">
            The warehouse stock record starts at zero. Set the real quantity from the stock action on the table.
          </p>
        )}

        <button type="submit" className="hidden" aria-hidden="true" tabIndex={-1} />
      </form>
    </Drawer>
  );
}

export default IngredientFormDrawer;
