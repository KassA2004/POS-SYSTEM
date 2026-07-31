import asyncpg
from fastapi import HTTPException, status
from app.models.warehouse_item_schemas import (
    WarehouseItemCreate,
    WarehouseItemUpdate,
    WarehouseItemResponse,
    WarehouseItemDeleteResponse,
)


async def create_warehouse_item_service(
    conn: asyncpg.Connection,
    data: WarehouseItemCreate,
) -> WarehouseItemResponse:
    """
    Creates a new warehouse item record in the active tenant schema.
    """
    query = """
        INSERT INTO warehouse_items (name, sku, unit_of_measure, minimum_stock)
        VALUES ($1, $2, $3, $4)
        RETURNING id, name, sku, unit_of_measure, minimum_stock;
    """
    try:
        row = await conn.fetchrow(
            query,
            data.name,
            data.sku,
            data.unit_of_measure,
            data.minimum_stock,
        )
        return WarehouseItemResponse(**dict(row))
    except asyncpg.exceptions.UniqueViolationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Warehouse item with SKU '{data.sku}' already exists.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create warehouse item: {str(e)}",
        )


async def update_warehouse_item_service(
    conn: asyncpg.Connection,
    item_id: int,
    data: WarehouseItemUpdate,
) -> WarehouseItemResponse:
    """
    Updates an existing warehouse item record in the active tenant schema.
    """
    existing = await conn.fetchrow("SELECT id FROM warehouse_items WHERE id = $1;", item_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Warehouse item with ID {item_id} not found.",
        )

    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        row = await conn.fetchrow(
            "SELECT id, name, sku, unit_of_measure, minimum_stock FROM warehouse_items WHERE id = $1;",
            item_id,
        )
        return WarehouseItemResponse(**dict(row))

    set_clauses = []
    values = []
    idx = 1
    for field, val in update_data.items():
        set_clauses.append(f"{field} = ${idx}")
        values.append(val)
        idx += 1

    values.append(item_id)
    query = f"""
        UPDATE warehouse_items
        SET {', '.join(set_clauses)}
        WHERE id = ${idx}
        RETURNING id, name, sku, unit_of_measure, minimum_stock;
    """

    try:
        row = await conn.fetchrow(query, *values)
        return WarehouseItemResponse(**dict(row))
    except asyncpg.exceptions.UniqueViolationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A warehouse item with the specified SKU already exists.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update warehouse item: {str(e)}",
        )


async def delete_warehouse_item_service(
    conn: asyncpg.Connection,
    item_id: int,
) -> WarehouseItemDeleteResponse:
    """
    Deletes a warehouse item record from the active tenant schema.
    """
    existing = await conn.fetchrow("SELECT id FROM warehouse_items WHERE id = $1;", item_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Warehouse item with ID {item_id} not found.",
        )

    try:
        await conn.execute("DELETE FROM warehouse_items WHERE id = $1;", item_id)
        return WarehouseItemDeleteResponse(
            message=f"Warehouse item {item_id} deleted successfully.",
            item_id=item_id,
        )
    except asyncpg.exceptions.ForeignKeyViolationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete warehouse item {item_id} because active references (e.g. inventory transactions or orders) exist.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete warehouse item: {str(e)}",
        )
