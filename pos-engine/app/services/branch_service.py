import asyncpg
from fastapi import HTTPException, status
from app.models.branch_schemas import BranchCreate, BranchResponse, BranchDeleteResponse


async def create_branch_service(
    conn: asyncpg.Connection,
    branch_data: BranchCreate,
) -> BranchResponse:
    """
    Creates a new branch in the active tenant schema.
    """
    query = """
        INSERT INTO branches (name, address, is_active)
        VALUES ($1, $2, $3)
        RETURNING id, name, address, is_active, created_at;
    """
    try:
        row = await conn.fetchrow(
            query,
            branch_data.name,
            branch_data.address,
            branch_data.is_active,
        )
        return BranchResponse(**dict(row))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create branch: {str(e)}",
        )


async def delete_branch_service(
    conn: asyncpg.Connection,
    branch_id: int,
) -> BranchDeleteResponse:
    """
    Deletes a branch by ID in the active tenant schema.
    """
    # 1. Check if branch exists in the isolated tenant schema
    existing = await conn.fetchrow("SELECT id FROM branches WHERE id = $1;", branch_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Branch with ID {branch_id} not found.",
        )

    # 2. Attempt deletion
    try:
        await conn.execute("DELETE FROM branches WHERE id = $1;", branch_id)
        return BranchDeleteResponse(
            message=f"Branch {branch_id} deleted successfully.",
            branch_id=branch_id,
        )
    except asyncpg.exceptions.ForeignKeyViolationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete branch {branch_id} because it has active dependencies (such as shifts or orders).",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete branch: {str(e)}",
        )
