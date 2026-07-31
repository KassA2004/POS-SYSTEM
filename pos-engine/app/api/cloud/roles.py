from fastapi import APIRouter, Depends, status
import asyncpg
from app.db.database import get_db_connection
from app.api.cloud.auth.dependencies import require_schema_owner
from app.models.role_schemas import RoleCreate, RoleUpdate, RoleResponse, RoleDeleteResponse
from app.services.role_service import (
    create_role_service,
    update_role_service,
    delete_role_service,
)

router = APIRouter(prefix="/roles", tags=["Cloud Roles & Permissions Management"])


@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    data: RoleCreate,
    current_user: dict = Depends(require_schema_owner),
    conn: asyncpg.Connection = Depends(get_db_connection),
):
    """
    Creates a new role with assigned permissions in the tenant's isolated schema.
    """
    return await create_role_service(conn, data)


@router.put("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    data: RoleUpdate,
    current_user: dict = Depends(require_schema_owner),
    conn: asyncpg.Connection = Depends(get_db_connection),
):
    """
    Updates a role name and/or its permission assignments in the tenant's isolated schema.
    """
    return await update_role_service(conn, role_id, data)


@router.delete("/{role_id}", response_model=RoleDeleteResponse)
async def delete_role(
    role_id: int,
    current_user: dict = Depends(require_schema_owner),
    conn: asyncpg.Connection = Depends(get_db_connection),
):
    """
    Deletes a role from the tenant's isolated schema if not currently assigned to active employees.
    """
    return await delete_role_service(conn, role_id)
