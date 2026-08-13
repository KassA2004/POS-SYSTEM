import { Drawer } from '@/globalComponents/Drawer';
import { Button } from '@/globalComponents/Button';
import { FormField, Input } from '@/globalComponents/Input';
import { Alert } from '@/globalComponents/Alert';
import { formatQuantity } from '@/lib/format';
import type { useIngredients } from '@/hooks/useIngredients';

export interface StockAdjustDrawerProps {
  state: ReturnType<typeof useIngredients>;
}

export function StockAdjustDrawer({ state }: StockAdjustDrawerProps) {
  const { stockTarget, stockValue, setStockValue, savingStock, stockError, closeStock, saveStock } = state;

  return (
    <Drawer
      open={stockTarget !== null}
      onClose={closeStock}
      title="Adjust warehouse stock"
      description={stockTarget ? stockTarget.name : undefined}
      footer={
        <>
          <Button variant="secondary" onClick={closeStock} disabled={savingStock}>
            Cancel
          </Button>
          <Button variant="primary" onClick={saveStock} loading={savingStock}>
            Save stock level
          </Button>
        </>
      }
    >
      <form
        className="space-y-5"
        onSubmit={(e) => {
          e.preventDefault();
          void saveStock();
        }}
      >
        {stockError && <Alert variant="danger">{stockError}</Alert>}

        {stockTarget && (
          <dl className="grid grid-cols-[minmax(120px,auto)_1fr] gap-x-6 gap-y-2 text-body-sm">
            <dt className="text-ink-secondary">Current stock</dt>
            <dd className="tabular-nums text-ink-primary">
              {formatQuantity(stockTarget.current_stock)} {stockTarget.unit_of_measure}
            </dd>
            <dt className="text-ink-secondary">Minimum</dt>
            <dd className="tabular-nums text-ink-primary">
              {formatQuantity(stockTarget.minimum_stock)} {stockTarget.unit_of_measure}
            </dd>
          </dl>
        )}

        <FormField
          label={`New quantity${stockTarget ? ` (${stockTarget.unit_of_measure})` : ''}`}
          required
          hint="This sets the absolute stock level, it does not add to the current amount."
        >
          <Input
            type="number"
            min="0"
            step="0.001"
            value={stockValue}
            onChange={(e) => setStockValue(e.target.value)}
            className="text-right tabular-nums"
            autoFocus
          />
        </FormField>

        <button type="submit" className="hidden" aria-hidden="true" tabIndex={-1} />
      </form>
    </Drawer>
  );
}

export default StockAdjustDrawer;
