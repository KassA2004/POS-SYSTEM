import asyncpg
from fastapi import HTTPException, status
from app.models.product_schemas import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductDeleteResponse,
)


async def create_product_service(
    conn: asyncpg.Connection,
    data: ProductCreate,
) -> ProductResponse:
    """
    Creates a new product record in the active tenant schema.
    """
    if data.direct_warehouse_item_id is not None:
        item = await conn.fetchrow(
            "SELECT id FROM warehouse_items WHERE id = $1;",
            data.direct_warehouse_item_id,
        )
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Direct warehouse item with ID {data.direct_warehouse_item_id} not found.",
            )

    query = """
        INSERT INTO products (name, price, is_recipe, direct_warehouse_item_id, is_active)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id, name, price, is_recipe, direct_warehouse_item_id, is_active, created_at;
    """
    try:
        row = await conn.fetchrow(
            query,
            data.name,
            data.price,
            data.is_recipe,
            data.direct_warehouse_item_id,
            data.is_active,
        )
        return ProductResponse(**dict(row))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create product: {str(e)}",
        )


async def update_product_service(
    conn: asyncpg.Connection,
    product_id: int,
    data: ProductUpdate,
) -> ProductResponse:
    """
    Updates an existing product record in the active tenant schema.
    """
    existing = await conn.fetchrow("SELECT id FROM products WHERE id = $1;", product_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found.",
        )

    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        row = await conn.fetchrow(
            "SELECT id, name, price, is_recipe, direct_warehouse_item_id, is_active, created_at FROM products WHERE id = $1;",
            product_id,
        )
        return ProductResponse(**dict(row))

    if "direct_warehouse_item_id" in update_data and update_data["direct_warehouse_item_id"] is not None:
        item = await conn.fetchrow(
            "SELECT id FROM warehouse_items WHERE id = $1;",
            update_data["direct_warehouse_item_id"],
        )
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Direct warehouse item with ID {update_data['direct_warehouse_item_id']} not found.",
            )

    set_clauses = []
    values = []
    idx = 1
    for field, val in update_data.items():
        set_clauses.append(f"{field} = ${idx}")
        values.append(val)
        idx += 1

    values.append(product_id)
    query = f"""
        UPDATE products
        SET {', '.join(set_clauses)}
        WHERE id = ${idx}
        RETURNING id, name, price, is_recipe, direct_warehouse_item_id, is_active, created_at;
    """

    try:
        row = await conn.fetchrow(query, *values)
        return ProductResponse(**dict(row))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update product: {str(e)}",
        )


async def delete_product_service(
    conn: asyncpg.Connection,
    product_id: int,
) -> ProductDeleteResponse:
    """
    Deletes a product record from the active tenant schema.
    """
    existing = await conn.fetchrow("SELECT id FROM products WHERE id = $1;", product_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found.",
        )

    try:
        await conn.execute("DELETE FROM products WHERE id = $1;", product_id)
        return ProductDeleteResponse(
            message=f"Product {product_id} deleted successfully.",
            product_id=product_id,
        )
    except asyncpg.exceptions.ForeignKeyViolationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete product {product_id} because active order records exist referencing this product.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete product: {str(e)}",
        )
