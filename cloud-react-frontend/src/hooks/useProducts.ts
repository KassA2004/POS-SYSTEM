import { useCallback, useState } from 'react';
import { productsApi, warehouseItemsApi } from '@/services/resources';
import { extractErrorMessage } from '@/services/api';
import { useResource } from './useResource';
import { useToast } from './useToast';
import { toNumber } from '@/lib/format';
import type { Product, ProductCreate, ProductDetail, WarehouseItem } from '@/types/domain';

const EMPTY_PRODUCTS: Product[] = [];
const EMPTY_ITEMS: WarehouseItem[] = [];

export interface ProductFormState {
  name: string;
  price: string;
  is_recipe: boolean;
  direct_warehouse_item_id: string;
  is_active: boolean;
}

export const emptyProductForm: ProductFormState = {
  name: '',
  price: '0.00',
  is_recipe: false,
  direct_warehouse_item_id: '',
  is_active: true,
};

export function useProducts() {
  const productsLoader = useCallback(() => productsApi.list(), []);
  const itemsLoader = useCallback(() => warehouseItemsApi.list(), []);

  const { data: products, loading, error, reload } = useResource<Product[]>(productsLoader, EMPTY_PRODUCTS);
  const { data: ingredients } = useResource<WarehouseItem[]>(itemsLoader, EMPTY_ITEMS);
  const { toast } = useToast();

  const [drawerOpen, setDrawerOpen] = useState(false);
  const [editing, setEditing] = useState<Product | null>(null);
  const [form, setForm] = useState<ProductFormState>(emptyProductForm);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  // --- recipe builder ---
  const [recipeProduct, setRecipeProduct] = useState<ProductDetail | null>(null);
  const [recipeLoading, setRecipeLoading] = useState(false);
  const [recipeError, setRecipeError] = useState<string | null>(null);
  const [newIngredientId, setNewIngredientId] = useState('');
  const [newQuantity, setNewQuantity] = useState('1');
  const [addingRecipe, setAddingRecipe] = useState(false);

  const [deleteTarget, setDeleteTarget] = useState<Product | null>(null);
  const [deleting, setDeleting] = useState(false);

  const openCreate = () => {
    setEditing(null);
    setForm(emptyProductForm);
    setFormError(null);
    setDrawerOpen(true);
  };

  const openEdit = (product: Product) => {
    setEditing(product);
    setForm({
      name: product.name,
      price: String(toNumber(product.price)),
      is_recipe: product.is_recipe,
      direct_warehouse_item_id: product.direct_warehouse_item_id ? String(product.direct_warehouse_item_id) : '',
      is_active: product.is_active,
    });
    setFormError(null);
    setDrawerOpen(true);
  };

  const closeDrawer = () => {
    setDrawerOpen(false);
    setEditing(null);
  };

  const updateForm = (patch: Partial<ProductFormState>) => setForm((prev) => ({ ...prev, ...patch }));

  const save = async () => {
    if (!form.name.trim()) {
      setFormError('Product name is required.');
      return;
    }
    const price = Number(form.price);
    if (!Number.isFinite(price) || price < 0) {
      setFormError('Price must be zero or greater.');
      return;
    }
    if (!form.is_recipe && !form.direct_warehouse_item_id) {
      setFormError('A direct product must be linked to the ingredient it draws stock from.');
      return;
    }

    setSaving(true);
    setFormError(null);
    try {
      const payload: ProductCreate = {
        name: form.name.trim(),
        price,
        is_recipe: form.is_recipe,
        is_active: form.is_active,
        // A recipe product draws stock from its recipe lines, never a direct item.
        direct_warehouse_item_id: form.is_recipe ? null : Number(form.direct_warehouse_item_id),
      };

      if (editing) {
        await productsApi.update(editing.id, payload);
        toast(`Product "${payload.name}" updated.`);
      } else {
        const created = await productsApi.create(payload);
        toast(`Product "${payload.name}" created.`);
        closeDrawer();
        await reload();
        // Recipe products are useless until they have ingredients - go straight there.
        if (created.is_recipe) {
          await openRecipe(created);
        }
        setSaving(false);
        return;
      }

      closeDrawer();
      await reload();
    } catch (err) {
      setFormError(extractErrorMessage(err));
    } finally {
      setSaving(false);
    }
  };

  const openRecipe = async (product: Product) => {
    setRecipeLoading(true);
    setRecipeError(null);
    setNewIngredientId('');
    setNewQuantity('1');
    try {
      const detail = await productsApi.get(product.id);
      setRecipeProduct(detail);
    } catch (err) {
      toast(extractErrorMessage(err), 'danger');
    } finally {
      setRecipeLoading(false);
    }
  };

  const refreshRecipe = async (productId: number) => {
    try {
      const detail = await productsApi.get(productId);
      setRecipeProduct(detail);
    } catch (err) {
      setRecipeError(extractErrorMessage(err));
    }
  };

  const closeRecipe = () => {
    setRecipeProduct(null);
    setRecipeError(null);
  };

  const addRecipeLine = async () => {
    if (!recipeProduct) return;
    if (!newIngredientId) {
      setRecipeError('Choose an ingredient.');
      return;
    }
    const quantity = Number(newQuantity);
    if (!Number.isFinite(quantity) || quantity <= 0) {
      setRecipeError('Quantity required must be greater than zero.');
      return;
    }
    // product_recipes has UNIQUE (product_id, warehouse_item_id).
    if (recipeProduct.recipes.some((r) => r.warehouse_item_id === Number(newIngredientId))) {
      setRecipeError('That ingredient is already in this recipe. Edit the existing line instead.');
      return;
    }

    setAddingRecipe(true);
    setRecipeError(null);
    try {
      await productsApi.addRecipe(recipeProduct.id, {
        warehouse_item_id: Number(newIngredientId),
        quantity_required: quantity,
      });
      setNewIngredientId('');
      setNewQuantity('1');
      await refreshRecipe(recipeProduct.id);
    } catch (err) {
      setRecipeError(extractErrorMessage(err));
    } finally {
      setAddingRecipe(false);
    }
  };

  const updateRecipeLine = async (recipeId: number, quantity: number) => {
    if (!recipeProduct) return;
    if (!Number.isFinite(quantity) || quantity <= 0) {
      setRecipeError('Quantity required must be greater than zero.');
      return;
    }
    try {
      await productsApi.updateRecipe(recipeProduct.id, recipeId, { quantity_required: quantity });
      await refreshRecipe(recipeProduct.id);
    } catch (err) {
      setRecipeError(extractErrorMessage(err));
    }
  };

  const removeRecipeLine = async (recipeId: number) => {
    if (!recipeProduct) return;
    try {
      await productsApi.removeRecipe(recipeProduct.id, recipeId);
      await refreshRecipe(recipeProduct.id);
    } catch (err) {
      setRecipeError(extractErrorMessage(err));
    }
  };

  const confirmDelete = async () => {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      await productsApi.remove(deleteTarget.id);
      toast(`Product "${deleteTarget.name}" deleted.`);
      setDeleteTarget(null);
      await reload();
    } catch (err) {
      toast(extractErrorMessage(err), 'danger');
    } finally {
      setDeleting(false);
    }
  };

  return {
    products,
    ingredients,
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

    recipeProduct,
    recipeLoading,
    recipeError,
    newIngredientId,
    setNewIngredientId,
    newQuantity,
    setNewQuantity,
    addingRecipe,
    openRecipe,
    closeRecipe,
    addRecipeLine,
    updateRecipeLine,
    removeRecipeLine,

    deleteTarget,
    setDeleteTarget,
    deleting,
    confirmDelete,
  };
}

export default useProducts;
