import { useCallback, useMemo, useState } from 'react';
import { inventoryApi, warehouseItemsApi } from '@/services/resources';
import { extractErrorMessage } from '@/services/api';
import { useResource } from './useResource';
import { useToast } from './useToast';
import { toNumber } from '@/lib/format';
import type { InventoryRecord, WarehouseItem, WarehouseItemCreate } from '@/types/domain';

const EMPTY_ITEMS: WarehouseItem[] = [];
const EMPTY_STOCK: InventoryRecord[] = [];

export interface IngredientFormState {
  name: string;
  sku: string;
  unit_of_measure: string;
  minimum_stock: string;
}

export const emptyIngredientForm: IngredientFormState = {
  name: '',
  sku: '',
  unit_of_measure: '',
  minimum_stock: '0',
};

export interface IngredientRow extends WarehouseItem {
  current_stock: number;
  is_low_stock: boolean;
  has_stock_record: boolean;
}

export function useIngredients() {
  const itemsLoader = useCallback(() => warehouseItemsApi.list(), []);
  const stockLoader = useCallback(() => inventoryApi.list(), []);

  const { data: items, loading, error, reload } = useResource<WarehouseItem[]>(itemsLoader, EMPTY_ITEMS);
  const { data: stock, reload: reloadStock } = useResource<InventoryRecord[]>(stockLoader, EMPTY_STOCK);
  const { toast } = useToast();

  const [drawerOpen, setDrawerOpen] = useState(false);
  const [editing, setEditing] = useState<WarehouseItem | null>(null);
  const [form, setForm] = useState<IngredientFormState>(emptyIngredientForm);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const [stockTarget, setStockTarget] = useState<IngredientRow | null>(null);
  const [stockValue, setStockValue] = useState('0');
  const [savingStock, setSavingStock] = useState(false);
  const [stockError, setStockError] = useState<string | null>(null);

  const [deleteTarget, setDeleteTarget] = useState<WarehouseItem | null>(null);
  const [deleting, setDeleting] = useState(false);

  /** Joins each item with its warehouse stock row and derives the low-stock flag. */
  const rows: IngredientRow[] = useMemo(() => {
    const stockByItem = new Map(stock.map((s) => [s.warehouse_item_id, toNumber(s.quantity)]));
    return items.map((item) => {
      const hasRecord = stockByItem.has(item.id);
      const current = stockByItem.get(item.id) ?? 0;
      return {
        ...item,
        current_stock: current,
        has_stock_record: hasRecord,
        is_low_stock: current <= toNumber(item.minimum_stock),
      };
    });
  }, [items, stock]);

  const lowStockCount = rows.filter((r) => r.is_low_stock).length;

  const openCreate = () => {
    setEditing(null);
    setForm(emptyIngredientForm);
    setFormError(null);
    setDrawerOpen(true);
  };

  const openEdit = (item: WarehouseItem) => {
    setEditing(item);
    setForm({
      name: item.name,
      sku: item.sku ?? '',
      unit_of_measure: item.unit_of_measure,
      minimum_stock: String(toNumber(item.minimum_stock)),
    });
    setFormError(null);
    setDrawerOpen(true);
  };

  const closeDrawer = () => {
    setDrawerOpen(false);
    setEditing(null);
  };

  const updateForm = (patch: Partial<IngredientFormState>) => setForm((prev) => ({ ...prev, ...patch }));

  const save = async () => {
    if (!form.name.trim()) {
      setFormError('Ingredient name is required.');
      return;
    }
    if (!form.unit_of_measure.trim()) {
      setFormError('Unit of measure is required (for example kg, L, pcs).');
      return;
    }
    const minimum = Number(form.minimum_stock);
    if (!Number.isFinite(minimum) || minimum < 0) {
      setFormError('Minimum stock must be zero or greater.');
      return;
    }

    setSaving(true);
    setFormError(null);
    try {
      const payload: WarehouseItemCreate = {
        name: form.name.trim(),
        unit_of_measure: form.unit_of_measure.trim(),
        minimum_stock: minimum,
      };
      // SKU is UNIQUE in Postgres, so send null rather than '' to avoid a
      // duplicate-key collision between two items that both have no SKU.
      payload.sku = form.sku.trim() ? form.sku.trim() : null;

      if (editing) {
        await warehouseItemsApi.update(editing.id, payload);
        toast(`Ingredient "${payload.name}" updated.`);
      } else {
        const created = await warehouseItemsApi.create(payload);
        // Create the stock row immediately so the item shows a real 0 rather
        // than an absent record the inventory endpoints would 404 on.
        try {
          await inventoryApi.initialise({ warehouse_item_id: created.id, quantity: 0 });
        } catch {
          // Non-fatal: the item exists, stock can be initialised from the table.
        }
        toast(`Ingredient "${payload.name}" created.`);
      }

      closeDrawer();
      await Promise.all([reload(), reloadStock()]);
    } catch (err) {
      setFormError(extractErrorMessage(err));
    } finally {
      setSaving(false);
    }
  };

  const openStock = (row: IngredientRow) => {
    setStockTarget(row);
    setStockValue(String(row.current_stock));
    setStockError(null);
  };

  const closeStock = () => setStockTarget(null);

  const saveStock = async () => {
    if (!stockTarget) return;
    const quantity = Number(stockValue);
    if (!Number.isFinite(quantity) || quantity < 0) {
      setStockError('Quantity must be zero or greater.');
      return;
    }

    setSavingStock(true);
    setStockError(null);
    try {
      if (stockTarget.has_stock_record) {
        await inventoryApi.setQuantity(stockTarget.id, quantity);
      } else {
        await inventoryApi.initialise({ warehouse_item_id: stockTarget.id, quantity });
      }
      toast(`Stock updated for "${stockTarget.name}".`);
      closeStock();
      await reloadStock();
    } catch (err) {
      setStockError(extractErrorMessage(err));
    } finally {
      setSavingStock(false);
    }
  };

  const confirmDelete = async () => {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      await warehouseItemsApi.remove(deleteTarget.id);
      toast(`Ingredient "${deleteTarget.name}" deleted.`);
      setDeleteTarget(null);
      await Promise.all([reload(), reloadStock()]);
    } catch (err) {
      toast(extractErrorMessage(err), 'danger');
    } finally {
      setDeleting(false);
    }
  };

  return {
    rows,
    items,
    lowStockCount,
    loading,
    error,
    reload,

    drawerOpen,
    editing,
    form,
    saving,
    formError,
    openCreate,
    openEdit,
    closeDrawer,
    updateForm,
    save,

    stockTarget,
    stockValue,
    setStockValue,
    savingStock,
    stockError,
    openStock,
    closeStock,
    saveStock,

    deleteTarget,
    setDeleteTarget,
    deleting,
    confirmDelete,
  };
}

export default useIngredients;
