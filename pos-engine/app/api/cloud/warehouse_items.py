from fastapi import APIRouter, Depends, status
import asyncpg
from app.db.database import get_db_connection
from app.api.cloud.auth.dependencies import require_schema_owner
from app.models.warehouse_item_schemas import (
    WarehouseItemCreate,
    WarehouseItemUpdate,
    WarehouseItemResponse,
    WarehouseItemDeleteResponse,
)
from app.services.warehouse_item_service import (
    create_warehouse_item_service,
    update_warehouse_item_service,
    delete_warehouse_item_service,
)

router = APIRouter(prefix="/warehouse-items", tags=["Cloud Warehouse Items"])


@router.post("/", response_model=WarehouseItemResponse, status_code=status.HTTP_201_CREATED)
async def create_warehouse_item(
    data: WarehouseItemCreate,
    current_user: dict = Depends(require_schema_owner),
    conn: asyncpg.Connection = Depends(get_db_connection),
):
    """
    Creates a new warehouse item in the tenant schema.
    Only accessible by schema owners (TENANT_OWNER / SUPER_ADMIN).
    """
    return await create_warehouse_item_service(conn, data)


@router.put("/{item_id}", response_model=WarehouseItemResponse)
async def update_warehouse_item(
    item_id: int,
    data: WarehouseItemUpdate,
    current_user: dict = Depends(require_schema_owner),
    conn: asyncpg.Connection = Depends(get_db_connection),
):
    """
    Updates a warehouse item by ID in the tenant schema.
    Only accessible by schema owners (TENANT_OWNER / SUPER_ADMIN).
    """
    return await update_warehouse_item_service(conn, item_id, data)


@router.delete("/{item_id}", response_model=WarehouseItemDeleteResponse)
async def delete_warehouse_item(
    item_id: int,
    current_user: dict = Depends(require_schema_owner),
    conn: asyncpg.Connection = Depends(get_db_connection),
):
    """
    Deletes a warehouse item by ID from the tenant schema.
    Only accessible by schema owners (TENANT_OWNER / SUPER_ADMIN).
    """
    return await delete_warehouse_item_service(conn, item_id)
