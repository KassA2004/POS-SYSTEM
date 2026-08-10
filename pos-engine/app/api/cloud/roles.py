from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.cloud.auth.dependencies import require_schema_owner, get_scoped_db
from app.models.role_schemas import RoleCreate, RoleUpdate, RoleResponse, PermissionOut, RoleDeleteResponse
from app.services.role_service import (
    create_role_service,
    get_roles_service,
    get_role_by_id_service,
    get_all_permissions_service,
    update_role_service,
    delete_role_service,
)

router = APIRouter(prefix="/roles", tags=["Cloud Roles & Permissions Management"])


@router.get("/", response_model=List[RoleResponse])
async def get_roles(
    current_user: dict = Depends(require_schema_owner),
    db: AsyncSession = Depends(get_scoped_db),
):
    """
    Retrieves all roles with their assigned permissions from the tenant's isolated schema.
    """
    return await get_roles_service(db)


@router.get("/permissions", response_model=List[PermissionOut])
async def get_permissions(
    current_user: dict = Depends(require_schema_owner),
    db: AsyncSession = Depends(get_scoped_db),
):
    """
    Retrieves the system reference list of all available permissions.
    """
    return await get_all_permissions_service(db)


@router.get("/{role_id}", response_model=RoleResponse)
async def get_role_by_id(
    role_id: int,
    current_user: dict = Depends(require_schema_owner),
    db: AsyncSession = Depends(get_scoped_db),
):
    """
    Retrieves a single role by ID with its assigned permissions from the tenant's isolated schema.
    """
    return await get_role_by_id_service(db, role_id)


@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)

async def create_role(
    data: RoleCreate,
    current_user: dict = Depends(require_schema_owner),
    db: AsyncSession = Depends(get_scoped_db),
):
    """
    Creates a new role with assigned permissions in the tenant's isolated schema.
    """
    return await create_role_service(db, data)


@router.put("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    data: RoleUpdate,
    current_user: dict = Depends(require_schema_owner),
    db: AsyncSession = Depends(get_scoped_db),
):
    """
    Updates a role name and/or its permission assignments in the tenant's isolated schema.
    """
    return await update_role_service(db, role_id, data)


@router.delete("/{role_id}", response_model=RoleDeleteResponse)
async def delete_role(
    role_id: int,
    current_user: dict = Depends(require_schema_owner),
    db: AsyncSession = Depends(get_scoped_db),
):
    """
    Deletes a role from the tenant's isolated schema if not currently assigned to active employees.
    """
    return await delete_role_service(db, role_id)
