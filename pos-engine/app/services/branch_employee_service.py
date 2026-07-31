import asyncpg
from fastapi import HTTPException, status
from app.models.branch_employee_schemas import (
    BranchEmployeeAssignRequest,
    BranchEmployeeUpdateRequest,
    BranchEmployeeResponse,
    BranchEmployeeDeleteResponse,
)


async def get_branch_employee_by_id(
    conn: asyncpg.Connection,
    assignment_id: int,
) -> BranchEmployeeResponse:
    """
    Helper function to query and enrich a branch employee mapping record.
    """
    query = """
        SELECT 
            be.id, be.employee_id, be.branch_id, be.role_id, be.assigned_at, be.removed_at,
            e.name AS employee_name,
            b.name AS branch_name,
            r.name AS role_name
        FROM branch_employees be
        JOIN employees e ON be.employee_id = e.id
        JOIN branches b ON be.branch_id = b.id
        LEFT JOIN roles r ON be.role_id = r.id
        WHERE be.id = $1;
    """
    row = await conn.fetchrow(query, assignment_id)
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Branch employee assignment with ID {assignment_id} not found.",
        )
    return BranchEmployeeResponse(**dict(row))


async def assign_employee_to_branch_service(
    conn: asyncpg.Connection,
    branch_id: int,
    data: BranchEmployeeAssignRequest,
) -> BranchEmployeeResponse:
    """
    Creates a new mapping in branch_employees linking employee_id, branch_id, and role_id.
    Prevents active duplicate assignment of the same employee to the same branch.
    """
    # 1. Verify branch existence
    branch = await conn.fetchrow("SELECT id FROM branches WHERE id = $1;", branch_id)
    if not branch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Branch with ID {branch_id} not found.",
        )

    # 2. Verify employee existence
    employee = await conn.fetchrow("SELECT id FROM employees WHERE id = $1;", data.employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {data.employee_id} not found.",
        )

    # 3. Verify role existence (if provided)
    if data.role_id is not None:
        role = await conn.fetchrow("SELECT id FROM roles WHERE id = $1;", data.role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role with ID {data.role_id} not found.",
            )

    # 4. Check for active duplicate assignment
    existing_active = await conn.fetchrow(
        "SELECT id FROM branch_employees WHERE employee_id = $1 AND branch_id = $2 AND removed_at IS NULL;",
        data.employee_id,
        branch_id,
    )
    if existing_active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Employee {data.employee_id} is already actively assigned to branch {branch_id}.",
        )

    # 5. Insert new assignment
    insert_query = """
        INSERT INTO branch_employees (employee_id, branch_id, role_id, assigned_at)
        VALUES ($1, $2, $3, CURRENT_TIMESTAMP)
        RETURNING id;
    """
    row = await conn.fetchrow(insert_query, data.employee_id, branch_id, data.role_id)
    new_id = row["id"]

    # 6. Return enriched assignment
    return await get_branch_employee_by_id(conn, new_id)


async def update_branch_employee_service(
    conn: asyncpg.Connection,
    assignment_id: int,
    data: BranchEmployeeUpdateRequest,
) -> BranchEmployeeResponse:
    """
    Updates an assignment record (e.g. promoting/changing role_id or branch_id).
    """
    # 1. Verify existence
    existing = await conn.fetchrow(
        "SELECT id, employee_id, branch_id, role_id FROM branch_employees WHERE id = $1;",
        assignment_id,
    )
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Branch employee assignment with ID {assignment_id} not found.",
        )

    if data.role_id is None and data.branch_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field (role_id or branch_id) must be provided for update.",
        )

    # 2. Verify new branch if provided
    if data.branch_id is not None:
        branch = await conn.fetchrow("SELECT id FROM branches WHERE id = $1;", data.branch_id)
        if not branch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Branch with ID {data.branch_id} not found.",
            )

    # 3. Verify new role if provided
    if data.role_id is not None:
        role = await conn.fetchrow("SELECT id FROM roles WHERE id = $1;", data.role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role with ID {data.role_id} not found.",
            )

    # 4. Perform update
    update_query = """
        UPDATE branch_employees
        SET role_id = COALESCE($1, role_id),
            branch_id = COALESCE($2, branch_id)
        WHERE id = $3;
    """
    await conn.execute(update_query, data.role_id, data.branch_id, assignment_id)

    # 5. Return enriched updated assignment
    return await get_branch_employee_by_id(conn, assignment_id)


async def delete_branch_employee_service(
    conn: asyncpg.Connection,
    assignment_id: int,
) -> BranchEmployeeDeleteResponse:
    """
    Removes an employee from a branch by setting removed_at timestamp.
    """
    # 1. Verify existence
    existing = await conn.fetchrow(
        "SELECT id, removed_at FROM branch_employees WHERE id = $1;",
        assignment_id,
    )
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Branch employee assignment with ID {assignment_id} not found.",
        )

    if existing["removed_at"] is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Branch employee assignment {assignment_id} has already been removed.",
        )

    # 2. Soft-remove by setting removed_at timestamp
    update_query = """
        UPDATE branch_employees
        SET removed_at = CURRENT_TIMESTAMP
        WHERE id = $1
        RETURNING removed_at;
    """
    row = await conn.fetchrow(update_query, assignment_id)

    return BranchEmployeeDeleteResponse(
        message=f"Employee assignment {assignment_id} successfully removed from branch.",
        id=assignment_id,
        removed_at=row["removed_at"],
    )
