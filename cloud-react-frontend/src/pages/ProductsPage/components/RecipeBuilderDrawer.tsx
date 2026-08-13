import { Minus, Plus, ChefHat } from 'lucide-react';
import { Drawer } from '@/globalComponents/Drawer';
import { Button } from '@/globalComponents/Button';
import { FormField, Input } from '@/globalComponents/Input';
import { Select } from '@/globalComponents/Select';
import { Alert } from '@/globalComponents/Alert';
import { EmptyState } from '@/globalComponents/EmptyState';
import { Spinner } from '@/globalComponents/Spinner';
import { toNumber } from '@/lib/format';
import type { useProducts } from '@/hooks/useProducts';

export interface RecipeBuilderDrawerProps {
  state: ReturnType<typeof useProducts>;
}

export function RecipeBuilderDrawer({ state }: RecipeBuilderDrawerProps) {
  const {
    recipeProduct,
    recipeLoading,
    recipeError,
    ingredients,
    newIngredientId,
    setNewIngredientId,
    newQuantity,
    setNewQuantity,
    addingRecipe,
    closeRecipe,
    addRecipeLine,
    updateRecipeLine,
    removeRecipeLine,
  } = state;

  const ingredientById = new Map(ingredients.map((i) => [i.id, i]));
  const usedIds = new Set(recipeProduct?.recipes.map((r) => r.warehouse_item_id) ?? []);
  const availableIngredients = ingredients.filter((i) => !usedIds.has(i.id));

  return (
    <Drawer
      open={recipeProduct !== null}
      onClose={closeRecipe}
      width="md"
      title="Recipe"
      description={
        recipeProduct
          ? `Ingredients deducted from the warehouse each time "${recipeProduct.name}" is sold.`
          : undefined
      }
      footer={
        <Button variant="secondary" onClick={closeRecipe}>
          Done
        </Button>
      }
    >
      <div className="space-y-6">
        {recipeError && <Alert variant="danger">{recipeError}</Alert>}

        {recipeLoading ? (
          <div className="flex justify-center py-12">
            <Spinner size={24} />
          </div>
        ) : (
          <>
            <section className="space-y-3">
              <div className="flex items-baseline justify-between">
                <h3 className="text-caption font-medium text-ink-secondary">Ingredient lines</h3>
                <span className="text-caption text-ink-tertiary">
                  {recipeProduct?.recipes.length ?? 0} ingredient
                  {(recipeProduct?.recipes.length ?? 0) === 1 ? '' : 's'}
                </span>
              </div>

              {(recipeProduct?.recipes.length ?? 0) === 0 ? (
                <div className="border border-border-subtle rounded-lg">
                  <EmptyState
                    icon={<ChefHat size={24} strokeWidth={1.5} />}
                    title="No ingredients yet"
                    message="Add at least one ingredient, otherwise selling this product deducts nothing from stock."
                  />
                </div>
              ) : (
                <ul className="space-y-2">
                  {recipeProduct?.recipes.map((line) => {
                    const ingredient = ingredientById.get(line.warehouse_item_id);
                    return (
                      <li
                        key={line.id}
                        className="flex items-center gap-3 border border-border-subtle rounded-lg p-3 bg-surface"
                      >
                        <span className="flex-1 min-w-0 text-body text-ink-primary truncate">
                          {ingredient?.name ?? `Item #${line.warehouse_item_id}`}
                        </span>

                        <Input
                          type="number"
                          min="0.001"
                          step="0.001"
                          defaultValue={toNumber(line.quantity_required)}
                          aria-label={`Quantity of ${ingredient?.name ?? 'ingredient'}`}
                          className="w-28 text-right tabular-nums"
                          onBlur={(e) => {
                            const next = Number(e.target.value);
                            if (next !== toNumber(line.quantity_required)) {
                              void updateRecipeLine(line.id, next);
                            }
                          }}
                        />

                        <span className="w-10 shrink-0 text-caption text-ink-tertiary">
                          {ingredient?.unit_of_measure ?? ''}
                        </span>

                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => removeRecipeLine(line.id)}
                          aria-label={`Remove ${ingredient?.name ?? 'ingredient'} from recipe`}
                          className="shrink-0 hover:text-danger-fg hover:bg-danger-bg"
                        >
                          <Minus size={16} strokeWidth={1.5} />
                        </Button>
                      </li>
                    );
                  })}
                </ul>
              )}
            </section>

            <section className="space-y-4 border-t border-border-subtle pt-6">
              <h3 className="text-caption font-medium text-ink-secondary">Add an ingredient</h3>

              {availableIngredients.length === 0 ? (
                <Alert variant="info">Every ingredient is already used in this recipe.</Alert>
              ) : (
                <div className="flex items-end gap-3">
                  <FormField label="Ingredient" className="flex-1 max-w-none">
                    <Select
                      value={newIngredientId}
                      onChange={(e) => setNewIngredientId(e.target.value)}
                      placeholder="Choose an ingredient"
                      options={availableIngredients.map((i) => ({
                        value: i.id,
                        label: `${i.name} (${i.unit_of_measure})`,
                      }))}
                    />
                  </FormField>

                  <FormField label="Quantity" className="w-32 max-w-none">
                    <Input
                      type="number"
                      min="0.001"
                      step="0.001"
                      value={newQuantity}
                      onChange={(e) => setNewQuantity(e.target.value)}
                      className="text-right tabular-nums"
                    />
                  </FormField>

                  <Button
                    variant="primary"
                    onClick={addRecipeLine}
                    loading={addingRecipe}
                    icon={<Plus size={16} strokeWidth={1.5} />}
                    className="shrink-0"
                  >
                    Add
                  </Button>
                </div>
              )}
            </section>
          </>
        )}
      </div>
    </Drawer>
  );
}

export default RecipeBuilderDrawer;
