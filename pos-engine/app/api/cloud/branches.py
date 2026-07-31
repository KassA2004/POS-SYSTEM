from fastapi import APIRouter, Depends, status
import asyncpg
from app.db.database import get_db_connection
from app.api.cloud.auth.dependencies import require_schema_owner
from app.models.branch_schemas import BranchCreate, BranchResponse, BranchDeleteResponse
from app.services.branch_service import create_branch_service, delete_branch_service

router = APIRouter(prefix="/branches", tags=["Cloud Branch Management"])


@router.post("/", response_model=BranchResponse, status_code=status.HTTP_201_CREATED)
async def create_branch(
    branch_data: BranchCreate,
    current_user: dict = Depends(require_schema_owner),
    conn: asyncpg.Connection = Depends(get_db_connection),
):
    """
    Creates a new branch in the isolated tenant schema.
    Only accessible by the schema owner (TENANT_OWNER / SUPER_ADMIN).
    """
    return await create_branch_service(conn, branch_data)


@router.delete("/{branch_id}", response_model=BranchDeleteResponse)
async def delete_branch(
    branch_id: int,
    current_user: dict = Depends(require_schema_owner),
    conn: asyncpg.Connection = Depends(get_db_connection),
):
    """
    Deletes a branch by ID from the isolated tenant schema.
    Only accessible by the schema owner (TENANT_OWNER / SUPER_ADMIN).
    """
    return await delete_branch_service(conn, branch_id)
