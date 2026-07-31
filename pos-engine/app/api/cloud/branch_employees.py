from fastapi import APIRouter, Depends, status
import asyncpg
from app.db.database import get_db_connection
from app.api.cloud.auth.dependencies import require_schema_owner
from app.models.branch_employee_schemas import (
    BranchEmployeeAssignRequest,
    BranchEmployeeUpdateRequest,
    BranchEmployeeResponse,
    BranchEmployeeDeleteResponse,
)
from app.services.branch_employee_service import (
    assign_employee_to_branch_service,
    update_branch_employee_service,
    delete_branch_employee_service,
)

router = APIRouter(tags=["Cloud Branch Employee Mapping"])


@router.post("/branches/{branch_id}/assign", response_model=BranchEmployeeResponse, status_code=status.HTTP_201_CREATED)
async def assign_employee_to_branch(
    branch_id: int,
    data: BranchEmployeeAssignRequest,
    current_user: dict = Depends(require_schema_owner),
    conn: asyncpg.Connection = Depends(get_db_connection),
):
    """
    Creates a mapping in branch_employees linking employee_id, branch_id, and role_id.
    """
    return await assign_employee_to_branch_service(conn, branch_id, data)


@router.put("/branch-employees/{assignment_id}", response_model=BranchEmployeeResponse)
async def update_branch_employee_assignment(
    assignment_id: int,
    data: BranchEmployeeUpdateRequest,
    current_user: dict = Depends(require_schema_owner),
    conn: asyncpg.Connection = Depends(get_db_connection),
):
    """
    Updates an assignment record (e.g. promoting an employee to a new role_id at that branch).
    """
    return await update_branch_employee_service(conn, assignment_id, data)


@router.delete("/branch-employees/{assignment_id}", response_model=BranchEmployeeDeleteResponse)
async def delete_branch_employee_assignment(
    assignment_id: int,
    current_user: dict = Depends(require_schema_owner),
    conn: asyncpg.Connection = Depends(get_db_connection),
):
    """
    Removes an employee from a branch by setting the removed_at timestamp.
    """
    return await delete_branch_employee_service(conn, assignment_id)
