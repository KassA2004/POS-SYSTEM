from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException, status
from app.db.models.tenant_models import BranchEmployee, Branch, Employee, Role
from app.models.branch_employee_schemas import (
    BranchEmployeeAssignRequest,
    BranchEmployeeUpdateRequest,
    BranchEmployeeResponse,
    BranchEmployeeDeleteResponse,
)


async def get_branch_employee_by_id(
    db: AsyncSession,
    assignment_id: int,
) -> BranchEmployeeResponse:
    """
    Helper that queries a branch_employee row and joins employee/branch/role names.
    """
    result = await db.execute(
        select(
            BranchEmployee.id,
            BranchEmployee.employee_id,
            BranchEmployee.branch_id,
            BranchEmployee.role_id,
            BranchEmployee.assigned_at,
            BranchEmployee.removed_at,
            Employee.name.label("employee_name"),
            Branch.name.label("branch_name"),
            Role.name.label("role_name"),
        )
        .join(Employee, BranchEmployee.employee_id == Employee.id)
        .join(Branch, BranchEmployee.branch_id == Branch.id)
        .outerjoin(Role, BranchEmployee.role_id == Role.id)
        .where(BranchEmployee.id == assignment_id)
    )
    row = result.first()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Branch employee assignment with ID {assignment_id} not found.",
        )

    return BranchEmployeeResponse(
        id=row.id,
        employee_id=row.employee_id,
        branch_id=row.branch_id,
        role_id=row.role_id,
        assigned_at=row.assigned_at,
        removed_at=row.removed_at,
        employee_name=row.employee_name,
        branch_name=row.branch_name,
        role_name=row.role_name,
    )


async def assign_employee_to_branch_service(
    db: AsyncSession,
    branch_id: int,
    data: BranchEmployeeAssignRequest,
) -> BranchEmployeeResponse:
    """
    Creates a new mapping in branch_employees linking employee_id, branch_id, and role_id.
    Prevents active duplicate assignment of the same employee to the same branch.
    """
    # 1. Verify branch existence
    branch_result = await db.execute(select(Branch.id).where(Branch.id == branch_id))
    if not branch_result.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Branch with ID {branch_id} not found.")

    # 2. Verify employee existence
    employee_result = await db.execute(select(Employee.id).where(Employee.id == data.employee_id))
    if not employee_result.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Employee with ID {data.employee_id} not found.")

    # 3. Verify role existence (if provided)
    if data.role_id is not None:
        role_result = await db.execute(select(Role.id).where(Role.id == data.role_id))
        if not role_result.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Role with ID {data.role_id} not found.")

    # 4. Check for active duplicate assignment
    active_result = await db.execute(
        select(BranchEmployee.id).where(
            BranchEmployee.employee_id == data.employee_id,
            BranchEmployee.branch_id == branch_id,
            BranchEmployee.removed_at.is_(None),
        )
    )
    if active_result.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Employee {data.employee_id} is already actively assigned to branch {branch_id}.",
        )

    # 5. Insert new assignment
    new_assignment = BranchEmployee(
        employee_id=data.employee_id,
        branch_id=branch_id,
        role_id=data.role_id,
    )
    db.add(new_assignment)
    await db.flush()

    return await get_branch_employee_by_id(db, new_assignment.id)


async def update_branch_employee_service(
    db: AsyncSession,
    assignment_id: int,
    data: BranchEmployeeUpdateRequest,
) -> BranchEmployeeResponse:
    """
    Updates an assignment record (e.g. promoting/changing role_id or branch_id).
    """
    result = await db.execute(select(BranchEmployee).where(BranchEmployee.id == assignment_id))
    assignment = result.scalar_one_or_none()

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Branch employee assignment with ID {assignment_id} not found.",
        )

    if data.role_id is None and data.branch_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field (role_id or branch_id) must be provided for update.",
        )

    # Verify new branch if provided
    if data.branch_id is not None:
        branch_result = await db.execute(select(Branch.id).where(Branch.id == data.branch_id))
        if not branch_result.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Branch with ID {data.branch_id} not found.")
        assignment.branch_id = data.branch_id

    # Verify new role if provided
    if data.role_id is not None:
        role_result = await db.execute(select(Role.id).where(Role.id == data.role_id))
        if not role_result.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Role with ID {data.role_id} not found.")
        assignment.role_id = data.role_id

    await db.flush()

    return await get_branch_employee_by_id(db, assignment_id)


async def delete_branch_employee_service(
    db: AsyncSession,
    assignment_id: int,
) -> BranchEmployeeDeleteResponse:
    """
    Removes an employee from a branch by setting removed_at timestamp (soft-delete).
    """
    result = await db.execute(select(BranchEmployee).where(BranchEmployee.id == assignment_id))
    assignment = result.scalar_one_or_none()

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Branch employee assignment with ID {assignment_id} not found.",
        )

    if assignment.removed_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Branch employee assignment {assignment_id} has already been removed.",
        )

    # Soft-remove: stamp removed_at with the database's current timestamp
    from sqlalchemy import func
    assignment.removed_at = func.now()
    await db.flush()
    await db.refresh(assignment)

    return BranchEmployeeDeleteResponse(
        message=f"Employee assignment {assignment_id} successfully removed from branch.",
        id=assignment_id,
        removed_at=assignment.removed_at,
    )
