from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.db.models.tenant_models import WarehouseItem
from app.models.warehouse_item_schemas import (
    WarehouseItemCreate,
    WarehouseItemUpdate,
    WarehouseItemResponse,
    WarehouseItemDeleteResponse,
)


async def get_warehouse_items_service(
    db: AsyncSession,
) -> List[WarehouseItemResponse]:
    """
    Retrieves all warehouse items in the active tenant schema.
    """
    result = await db.execute(select(WarehouseItem).order_by(WarehouseItem.id.asc()))
    items = result.scalars().all()
    return [WarehouseItemResponse.model_validate(i) for i in items]


async def get_warehouse_item_by_id_service(
    db: AsyncSession,
    item_id: int,
) -> WarehouseItemResponse:
    """
    Retrieves a single warehouse item by ID in the active tenant schema.
    """
    result = await db.execute(select(WarehouseItem).where(WarehouseItem.id == item_id))
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Warehouse item with ID {item_id} not found.",
        )

    return WarehouseItemResponse.model_validate(item)



async def create_warehouse_item_service(
    db: AsyncSession,
    data: WarehouseItemCreate,
) -> WarehouseItemResponse:
    """
    Creates a new warehouse item record in the active tenant schema.
    """
    new_item = WarehouseItem(
        name=data.name,
        sku=data.sku,
        unit_of_measure=data.unit_of_measure,
        minimum_stock=data.minimum_stock,
    )
    db.add(new_item)

    try:
        await db.flush()
        await db.refresh(new_item)
        return WarehouseItemResponse(
            id=new_item.id,
            name=new_item.name,
            sku=new_item.sku,
            unit_of_measure=new_item.unit_of_measure,
            minimum_stock=new_item.minimum_stock,
        )
    except IntegrityError:
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
    db: AsyncSession,
    item_id: int,
    data: WarehouseItemUpdate,
) -> WarehouseItemResponse:
    """
    Updates an existing warehouse item record in the active tenant schema.
    """
    result = await db.execute(select(WarehouseItem).where(WarehouseItem.id == item_id))
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Warehouse item with ID {item_id} not found.",
        )

    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        return WarehouseItemResponse(
            id=item.id,
            name=item.name,
            sku=item.sku,
            unit_of_measure=item.unit_of_measure,
            minimum_stock=item.minimum_stock,
        )

    for field, value in update_data.items():
        setattr(item, field, value)

    try:
        await db.flush()
        await db.refresh(item)
        return WarehouseItemResponse(
            id=item.id,
            name=item.name,
            sku=item.sku,
            unit_of_measure=item.unit_of_measure,
            minimum_stock=item.minimum_stock,
        )
    except IntegrityError:
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
    db: AsyncSession,
    item_id: int,
) -> WarehouseItemDeleteResponse:
    """
    Deletes a warehouse item record from the active tenant schema.
    """
    result = await db.execute(select(WarehouseItem).where(WarehouseItem.id == item_id))
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Warehouse item with ID {item_id} not found.",
        )

    try:
        await db.delete(item)
        await db.flush()
        return WarehouseItemDeleteResponse(
            message=f"Warehouse item {item_id} deleted successfully.",
            item_id=item_id,
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete warehouse item {item_id} because active references (e.g. inventory transactions or orders) exist.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete warehouse item: {str(e)}",
        )
