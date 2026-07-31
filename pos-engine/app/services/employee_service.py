import asyncpg
from fastapi import HTTPException, status
from app.models.employee_schemas import EmployeeCreate, EmployeeUpdate, EmployeeResponse, EmployeeDeleteResponse


async def create_employee_service(
    conn: asyncpg.Connection,
    data: EmployeeCreate,
) -> EmployeeResponse:
    """
    Creates a new employee record in the tenant's isolated schema.
    """
    query = """
        INSERT INTO employees (name, date_of_birth, phone)
        VALUES ($1, $2, $3)
        RETURNING id, name, date_of_birth, phone, created_at;
    """
    try:
        row = await conn.fetchrow(query, data.name, data.date_of_birth, data.phone)
        return EmployeeResponse(**dict(row))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create employee: {str(e)}",
        )


async def update_employee_service(
    conn: asyncpg.Connection,
    employee_id: int,
    data: EmployeeUpdate,
) -> EmployeeResponse:
    """
    Updates an existing employee record in the tenant's isolated schema.
    """
    # 1. Verify existence
    existing = await conn.fetchrow("SELECT id FROM employees WHERE id = $1;", employee_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {employee_id} not found.",
        )

    # 2. Build set fields dynamically from updated attributes
    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        # No fields sent to update; fetch current record and return
        row = await conn.fetchrow(
            "SELECT id, name, date_of_birth, phone, created_at FROM employees WHERE id = $1;",
            employee_id,
        )
        return EmployeeResponse(**dict(row))

    set_clauses = []
    values = []
    idx = 1
    for field, val in update_data.items():
        set_clauses.append(f"{field} = ${idx}")
        values.append(val)
        idx += 1

    values.append(employee_id)
    query = f"""
        UPDATE employees
        SET {', '.join(set_clauses)}
        WHERE id = ${idx}
        RETURNING id, name, date_of_birth, phone, created_at;
    """

    try:
        row = await conn.fetchrow(query, *values)
        return EmployeeResponse(**dict(row))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update employee: {str(e)}",
        )


async def delete_employee_service(
    conn: asyncpg.Connection,
    employee_id: int,
) -> EmployeeDeleteResponse:
    """
    Deletes an employee record from the tenant's isolated schema.
    """
    # 1. Verify existence
    existing = await conn.fetchrow("SELECT id FROM employees WHERE id = $1;", employee_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {employee_id} not found.",
        )

    # 2. Perform deletion
    try:
        await conn.execute("DELETE FROM employees WHERE id = $1;", employee_id)
        return EmployeeDeleteResponse(
            message=f"Employee {employee_id} deleted successfully.",
            employee_id=employee_id,
        )
    except asyncpg.exceptions.ForeignKeyViolationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete employee {employee_id} because associated active records (such as shifts or orders) exist.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete employee: {str(e)}",
        )
