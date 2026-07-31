import asyncpg
from fastapi import HTTPException, status
from app.models.product_recipe_schemas import (
    ProductRecipeCreate,
    ProductRecipeUpdate,
    ProductRecipeResponse,
    ProductRecipeDeleteResponse,
)


async def create_product_recipe_service(
    conn: asyncpg.Connection,
    product_id: int,
    data: ProductRecipeCreate,
) -> ProductRecipeResponse:
    """
    Adds a new recipe ingredient to a product and ensures product is flagged as a recipe.
    """
    # 1. Verify parent product exists
    product = await conn.fetchrow("SELECT id FROM products WHERE id = $1;", product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found.",
        )

    # 2. Verify warehouse item exists
    item = await conn.fetchrow("SELECT id FROM warehouse_items WHERE id = $1;", data.warehouse_item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Warehouse item with ID {data.warehouse_item_id} not found.",
        )

    query = """
        INSERT INTO product_recipes (product_id, warehouse_item_id, quantity_required)
        VALUES ($1, $2, $3)
        RETURNING id, product_id, warehouse_item_id, quantity_required;
    """
    try:
        row = await conn.fetchrow(query, product_id, data.warehouse_item_id, data.quantity_required)
        
        # Flag product as a recipe if not already
        await conn.execute("UPDATE products SET is_recipe = TRUE WHERE id = $1;", product_id)

        return ProductRecipeResponse(**dict(row))
    except asyncpg.exceptions.UniqueViolationError:
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
    conn: asyncpg.Connection,
    product_id: int,
    recipe_id: int,
    data: ProductRecipeUpdate,
) -> ProductRecipeResponse:
    """
    Updates an existing product recipe ingredient record.
    """
    existing = await conn.fetchrow(
        "SELECT id FROM product_recipes WHERE id = $1 AND product_id = $2;",
        recipe_id,
        product_id,
    )
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe entry with ID {recipe_id} for product {product_id} not found.",
        )

    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        row = await conn.fetchrow(
            "SELECT id, product_id, warehouse_item_id, quantity_required FROM product_recipes WHERE id = $1;",
            recipe_id,
        )
        return ProductRecipeResponse(**dict(row))

    if "warehouse_item_id" in update_data and update_data["warehouse_item_id"] is not None:
        item = await conn.fetchrow(
            "SELECT id FROM warehouse_items WHERE id = $1;",
            update_data["warehouse_item_id"],
        )
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Warehouse item with ID {update_data['warehouse_item_id']} not found.",
            )

    set_clauses = []
    values = []
    idx = 1
    for field, val in update_data.items():
        set_clauses.append(f"{field} = ${idx}")
        values.append(val)
        idx += 1

    values.append(recipe_id)
    values.append(product_id)
    query = f"""
        UPDATE product_recipes
        SET {', '.join(set_clauses)}
        WHERE id = ${idx} AND product_id = ${idx + 1}
        RETURNING id, product_id, warehouse_item_id, quantity_required;
    """

    try:
        row = await conn.fetchrow(query, *values)
        return ProductRecipeResponse(**dict(row))
    except asyncpg.exceptions.UniqueViolationError:
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
    conn: asyncpg.Connection,
    product_id: int,
    recipe_id: int,
) -> ProductRecipeDeleteResponse:
    """
    Deletes a product recipe ingredient record.
    """
    existing = await conn.fetchrow(
        "SELECT id FROM product_recipes WHERE id = $1 AND product_id = $2;",
        recipe_id,
        product_id,
    )
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe entry with ID {recipe_id} for product {product_id} not found.",
        )

    try:
        await conn.execute("DELETE FROM product_recipes WHERE id = $1;", recipe_id)
        
        # If no recipes remain for product, reset is_recipe flag to FALSE
        remaining = await conn.fetchval(
            "SELECT COUNT(*) FROM product_recipes WHERE product_id = $1;",
            product_id,
        )
        if remaining == 0:
            await conn.execute("UPDATE products SET is_recipe = FALSE WHERE id = $1;", product_id)

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
