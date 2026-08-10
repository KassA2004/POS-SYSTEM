from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.cloud.auth.dependencies import require_schema_owner, get_scoped_db
from app.models.branch_schemas import BranchCreate, BranchUpdate, BranchResponse, BranchDeleteResponse
from app.services.branch_service import (
    create_branch_service,
    get_branches_service,
    get_branch_by_id_service,
    update_branch_service,
    delete_branch_service,
)

router = APIRouter(prefix="/branches", tags=["Cloud Branch Management"])


@router.get("/", response_model=List[BranchResponse])
async def get_branches(
    current_user: dict = Depends(require_schema_owner),
    db: AsyncSession = Depends(get_scoped_db),
):
    """
    Retrieves all branches in the isolated tenant schema.
    Only accessible by the schema owner (TENANT_OWNER / SUPER_ADMIN).
    """
    return await get_branches_service(db)


@router.get("/{branch_id}", response_model=BranchResponse)
async def get_branch_by_id(
    branch_id: int,
    current_user: dict = Depends(require_schema_owner),
    db: AsyncSession = Depends(get_scoped_db),
):
    """
    Retrieves a single branch by ID from the isolated tenant schema.
    Only accessible by the schema owner (TENANT_OWNER / SUPER_ADMIN).
    """
    return await get_branch_by_id_service(db, branch_id)



@router.post("/", response_model=BranchResponse, status_code=status.HTTP_201_CREATED)
async def create_branch(
    branch_data: BranchCreate,
    current_user: dict = Depends(require_schema_owner),
    db: AsyncSession = Depends(get_scoped_db),
):
    """
    Creates a new branch in the isolated tenant schema.
    Only accessible by the schema owner (TENANT_OWNER / SUPER_ADMIN).
    """
    return await create_branch_service(db, branch_data)


@router.put("/{branch_id}", response_model=BranchResponse)
async def update_branch(
    branch_id: int,
    branch_data: BranchUpdate,
    current_user: dict = Depends(require_schema_owner),
    db: AsyncSession = Depends(get_scoped_db),
):
    """
    Updates a branch by ID in the isolated tenant schema.
    Only accessible by the schema owner (TENANT_OWNER / SUPER_ADMIN).
    """
    return await update_branch_service(db, branch_id, branch_data)


@router.delete("/{branch_id}", response_model=BranchDeleteResponse)

async def delete_branch(
    branch_id: int,
    current_user: dict = Depends(require_schema_owner),
    db: AsyncSession = Depends(get_scoped_db),
):
    """
    Deletes a branch by ID from the isolated tenant schema.
    Only accessible by the schema owner (TENANT_OWNER / SUPER_ADMIN).
    """
    return await delete_branch_service(db, branch_id)
