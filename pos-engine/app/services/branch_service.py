from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.db.models.tenant_models import Branch
from app.models.branch_schemas import BranchCreate, BranchUpdate, BranchResponse, BranchDeleteResponse


async def get_branches_service(
    db: AsyncSession,
) -> List[BranchResponse]:
    """
    Retrieves all branches in the active tenant schema.
    """
    result = await db.execute(select(Branch).order_by(Branch.id.asc()))
    branches = result.scalars().all()
    return [BranchResponse.model_validate(b) for b in branches]


async def get_branch_by_id_service(
    db: AsyncSession,
    branch_id: int,
) -> BranchResponse:
    """
    Retrieves a single branch by ID in the active tenant schema.
    """
    result = await db.execute(select(Branch).where(Branch.id == branch_id))
    branch = result.scalar_one_or_none()

    if not branch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Branch with ID {branch_id} not found.",
        )

    return BranchResponse.model_validate(branch)


async def update_branch_service(
    db: AsyncSession,
    branch_id: int,
    data: BranchUpdate,
) -> BranchResponse:
    """
    Updates an existing branch record in the active tenant schema.
    """
    result = await db.execute(select(Branch).where(Branch.id == branch_id))
    branch = result.scalar_one_or_none()

    if not branch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Branch with ID {branch_id} not found.",
        )

    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        return BranchResponse.model_validate(branch)

    for field, value in update_data.items():
        setattr(branch, field, value)

    try:
        await db.flush()
        await db.refresh(branch)
        return BranchResponse.model_validate(branch)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update branch: {str(e)}",
        )



async def create_branch_service(
    db: AsyncSession,
    branch_data: BranchCreate,
) -> BranchResponse:
    """
    Creates a new branch in the active tenant schema.
    """
    new_branch = Branch(
        name=branch_data.name,
        address=branch_data.address,
        is_active=branch_data.is_active,
    )
    db.add(new_branch)

    try:
        await db.flush()  # get the generated id before commit
        await db.refresh(new_branch)
        return BranchResponse(
            id=new_branch.id,
            name=new_branch.name,
            address=new_branch.address,
            is_active=new_branch.is_active,
            created_at=new_branch.created_at,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create branch: {str(e)}",
        )


async def delete_branch_service(
    db: AsyncSession,
    branch_id: int,
) -> BranchDeleteResponse:
    """
    Deletes a branch by ID in the active tenant schema.
    """
    result = await db.execute(select(Branch).where(Branch.id == branch_id))
    branch = result.scalar_one_or_none()

    if not branch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Branch with ID {branch_id} not found.",
        )

    try:
        await db.delete(branch)
        await db.flush()
        return BranchDeleteResponse(
            message=f"Branch {branch_id} deleted successfully.",
            branch_id=branch_id,
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete branch {branch_id} because it has active dependencies (such as shifts or orders).",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete branch: {str(e)}",
        )
