from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.db.models.tenant_models import InventoryWarehouse, WarehouseItem
from app.models.inventory_warehouse_schemas import InventoryWarehouseCreate, InventoryWarehouseUpdate


async def get_stock_level(
    db: AsyncSession,
    warehouse_item_id: int,
) -> InventoryWarehouse:
    """
    Fetches the inventory record for a given warehouse item.
    """
    result = await db.execute(
        select(InventoryWarehouse).where(
            InventoryWarehouse.warehouse_item_id == warehouse_item_id
        )
    )
    inventory = result.scalar_one_or_none()

    if not inventory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory record for warehouse item {warehouse_item_id} not found.",
        )
    return inventory


async def get_all_stock_levels(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
):
    """
    Returns all inventory records with optional pagination.
    """
    result = await db.execute(
        select(InventoryWarehouse).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def update_stock_level(
    db: AsyncSession,
    warehouse_item_id: int,
    update_data: InventoryWarehouseUpdate,
) -> InventoryWarehouse:
    """
    Updates the quantity for an existing inventory record.
    """
    inventory = await get_stock_level(db, warehouse_item_id)
    inventory.quantity = update_data.quantity
    await db.flush()
    await db.refresh(inventory)
    return inventory


async def create_stock_record(
    db: AsyncSession,
    data: InventoryWarehouseCreate,
) -> InventoryWarehouse:
    """
    Creates a new inventory record. Verifies the warehouse item exists first.
    """
    item_result = await db.execute(
        select(WarehouseItem.id).where(WarehouseItem.id == data.warehouse_item_id)
    )
    if not item_result.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Warehouse item with ID {data.warehouse_item_id} not found.",
        )

    new_inventory = InventoryWarehouse(
        warehouse_item_id=data.warehouse_item_id,
        quantity=data.quantity,
    )
    db.add(new_inventory)

    try:
        await db.flush()
        await db.refresh(new_inventory)
        return new_inventory
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create inventory record. An inventory record for this warehouse item may already exist.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create inventory record: {str(e)}",
        )