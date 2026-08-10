from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.db.models.tenant_models import ProductRecipe, Product, WarehouseItem
from app.models.product_recipe_schemas import (
    ProductRecipeCreate,
    ProductRecipeUpdate,
    ProductRecipeResponse,
    ProductRecipeDeleteResponse,
)


async def create_product_recipe_service(
    db: AsyncSession,
    product_id: int,
    data: ProductRecipeCreate,
) -> ProductRecipeResponse:
    """
    Adds a new recipe ingredient to a product and ensures product is flagged as a recipe.
    """
    # 1. Verify parent product exists
    product_result = await db.execute(select(Product).where(Product.id == product_id))
    product = product_result.scalar_one_or_none()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found.",
        )

    # 2. Verify warehouse item exists
    item_result = await db.execute(
        select(WarehouseItem.id).where(WarehouseItem.id == data.warehouse_item_id)
    )
    if not item_result.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Warehouse item with ID {data.warehouse_item_id} not found.",
        )

    new_recipe = ProductRecipe(
        product_id=product_id,
        warehouse_item_id=data.warehouse_item_id,
        quantity_required=data.quantity_required,
    )
    db.add(new_recipe)

    try:
        await db.flush()

        # Flag product as a recipe if not already
        if not product.is_recipe:
            product.is_recipe = True

        await db.refresh(new_recipe)
        return ProductRecipeResponse(
            id=new_recipe.id,
            product_id=new_recipe.product_id,
            warehouse_item_id=new_recipe.warehouse_item_id,
            quantity_required=new_recipe.quantity_required,
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Recipe ingredient for warehouse item ID {data.warehouse_item_id} already exists for product {product_id}.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add recipe ingredient: {str(e)}",
        )


async def update_product_recipe_service(
    db: AsyncSession,
    product_id: int,
    recipe_id: int,
    data: ProductRecipeUpdate,
) -> ProductRecipeResponse:
    """
    Updates an existing product recipe ingredient record.
    """
    result = await db.execute(
        select(ProductRecipe).where(
            ProductRecipe.id == recipe_id,
            ProductRecipe.product_id == product_id,
        )
    )
    recipe = result.scalar_one_or_none()

    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe entry with ID {recipe_id} for product {product_id} not found.",
        )

    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        return ProductRecipeResponse(
            id=recipe.id,
            product_id=recipe.product_id,
            warehouse_item_id=recipe.warehouse_item_id,
            quantity_required=recipe.quantity_required,
        )

    if "warehouse_item_id" in update_data and update_data["warehouse_item_id"] is not None:
        item_result = await db.execute(
            select(WarehouseItem.id).where(WarehouseItem.id == update_data["warehouse_item_id"])
        )
        if not item_result.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Warehouse item with ID {update_data['warehouse_item_id']} not found.",
            )

    for field, value in update_data.items():
        setattr(recipe, field, value)

    try:
        await db.flush()
        await db.refresh(recipe)
        return ProductRecipeResponse(
            id=recipe.id,
            product_id=recipe.product_id,
            warehouse_item_id=recipe.warehouse_item_id,
            quantity_required=recipe.quantity_required,
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A recipe ingredient with this warehouse item already exists for this product.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update recipe ingredient: {str(e)}",
        )


async def delete_product_recipe_service(
    db: AsyncSession,
    product_id: int,
    recipe_id: int,
) -> ProductRecipeDeleteResponse:
    """
    Deletes a product recipe ingredient record.
    If no recipes remain, resets is_recipe flag to False on the parent product.
    """
    result = await db.execute(
        select(ProductRecipe).where(
            ProductRecipe.id == recipe_id,
            ProductRecipe.product_id == product_id,
        )
    )
    recipe = result.scalar_one_or_none()

    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe entry with ID {recipe_id} for product {product_id} not found.",
        )

    try:
        await db.delete(recipe)
        await db.flush()

        # Count remaining recipes for this product
        count_result = await db.execute(
            select(func.count()).where(ProductRecipe.product_id == product_id)
        )
        remaining = count_result.scalar()

        if remaining == 0:
            product_result = await db.execute(select(Product).where(Product.id == product_id))
            product = product_result.scalar_one_or_none()
            if product:
                product.is_recipe = False

        return ProductRecipeDeleteResponse(
            message=f"Recipe entry {recipe_id} for product {product_id} deleted successfully.",
            recipe_id=recipe_id,
            product_id=product_id,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete recipe entry: {str(e)}",
        )
