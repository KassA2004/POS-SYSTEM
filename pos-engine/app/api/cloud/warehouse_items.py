from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.cloud.auth.dependencies import require_schema_owner, get_scoped_db
from app.models.warehouse_item_schemas import (
    WarehouseItemCreate,
    WarehouseItemUpdate,
    WarehouseItemResponse,
    WarehouseItemDeleteResponse,
)
from app.services.warehouse_item_service import (
    create_warehouse_item_service,
    get_warehouse_items_service,
    get_warehouse_item_by_id_service,
    update_warehouse_item_service,
    delete_warehouse_item_service,
)

router = APIRouter(prefix="/warehouse-items", tags=["Cloud Warehouse Items"])


@router.get("/", response_model=List[WarehouseItemResponse])
async def get_warehouse_items(
    current_user: dict = Depends(require_schema_owner),
    db: AsyncSession = Depends(get_scoped_db),
):
    """
    Retrieves all warehouse items in the tenant schema.
    Only accessible by schema owners (TENANT_OWNER / SUPER_ADMIN).
    """
    return await get_warehouse_items_service(db)


@router.get("/{item_id}", response_model=WarehouseItemResponse)
async def get_warehouse_item_by_id(
    item_id: int,
    current_user: dict = Depends(require_schema_owner),
    db: AsyncSession = Depends(get_scoped_db),
):
    """
    Retrieves a single warehouse item by ID in the tenant schema.
    Only accessible by schema owners (TENANT_OWNER / SUPER_ADMIN).
    """
    return await get_warehouse_item_by_id_service(db, item_id)


@router.post("/", response_model=WarehouseItemResponse, status_code=status.HTTP_201_CREATED)

async def create_warehouse_item(
    data: WarehouseItemCreate,
    current_user: dict = Depends(require_schema_owner),
    db: AsyncSession = Depends(get_scoped_db),
):
    """
    Creates a new warehouse item in the tenant schema.
    Only accessible by schema owners (TENANT_OWNER / SUPER_ADMIN).
    """
    return await create_warehouse_item_service(db, data)


@router.put("/{item_id}", response_model=WarehouseItemResponse)
async def update_warehouse_item(
    item_id: int,
    data: WarehouseItemUpdate,
    current_user: dict = Depends(require_schema_owner),
    db: AsyncSession = Depends(get_scoped_db),
):
    """
    Updates a warehouse item by ID in the tenant schema.
    Only accessible by schema owners (TENANT_OWNER / SUPER_ADMIN).
    """
    return await update_warehouse_item_service(db, item_id, data)


@router.delete("/{item_id}", response_model=WarehouseItemDeleteResponse)
async def delete_warehouse_item(
    item_id: int,
    current_user: dict = Depends(require_schema_owner),
    db: AsyncSession = Depends(get_scoped_db),
):
    """
    Deletes a warehouse item by ID from the tenant schema.
    Only accessible by schema owners (TENANT_OWNER / SUPER_ADMIN).
    """
    return await delete_warehouse_item_service(db, item_id)
