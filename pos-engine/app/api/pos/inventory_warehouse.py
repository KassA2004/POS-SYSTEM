from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.cloud.auth.dependencies import require_schema_owner, get_scoped_db
from app.models.inventory_warehouse_schemas import (
    InventoryWarehouseResponse,
    InventoryWarehouseUpdate,
    InventoryWarehouseCreate
)
from app.services.inventory_warehouse_service import (
    get_all_stock_levels,
    get_stock_level,
    update_stock_level,
    create_stock_record,
)

router = APIRouter(
    prefix="/pos/inventory",
    tags=["POS Inventory Warehouse"]
)


@router.get("/", response_model=List[InventoryWarehouseResponse])
async def get_all_inventory(
    skip: int = 0, 
    limit: int = 100,
    current_user: dict = Depends(require_schema_owner),
    db: AsyncSession = Depends(get_scoped_db),
):
    """Retrieve all inventory stock levels."""
    records = await get_all_stock_levels(db, skip=skip, limit=limit)
    return [InventoryWarehouseResponse.model_validate(r) for r in records]


@router.get("/{warehouse_item_id}", response_model=InventoryWarehouseResponse)
async def get_inventory_item(
    warehouse_item_id: int,
    current_user: dict = Depends(require_schema_owner),
    db: AsyncSession = Depends(get_scoped_db),
):
    """Check stock level for a specific warehouse item."""
    record = await get_stock_level(db, warehouse_item_id)
    return InventoryWarehouseResponse.model_validate(record)


@router.put("/{warehouse_item_id}", response_model=InventoryWarehouseResponse)
async def update_inventory_item(
    warehouse_item_id: int,
    inventory_update: InventoryWarehouseUpdate,
    current_user: dict = Depends(require_schema_owner),
    db: AsyncSession = Depends(get_scoped_db),
):
    """Update the stock quantity for a warehouse item (e.g., manual adjustment)."""
    record = await update_stock_level(db, warehouse_item_id, inventory_update)
    return InventoryWarehouseResponse.model_validate(record)


@router.post("/", response_model=InventoryWarehouseResponse, status_code=status.HTTP_201_CREATED)
async def initialize_inventory_item(
    inventory_create: InventoryWarehouseCreate,
    current_user: dict = Depends(require_schema_owner),
    db: AsyncSession = Depends(get_scoped_db),
):
    """Initialize a stock record for a newly created warehouse item."""
    record = await create_stock_record(db, inventory_create)
    return InventoryWarehouseResponse.model_validate(record)