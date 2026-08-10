from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.db.models.tenant_models import Employee
from app.models.employee_schemas import EmployeeCreate, EmployeeUpdate, EmployeeResponse, EmployeeDeleteResponse
from app.core.security import hash_password


async def get_employees_service(
    db: AsyncSession,
) -> List[EmployeeResponse]:
    """
    Retrieves all employee records in the tenant's isolated schema.
    """
    result = await db.execute(select(Employee).order_by(Employee.id.asc()))
    employees = result.scalars().all()
    return [EmployeeResponse.model_validate(e) for e in employees]


async def get_employee_by_id_service(
    db: AsyncSession,
    employee_id: int,
) -> EmployeeResponse:
    """
    Retrieves a single employee record by ID in the tenant's isolated schema.
    """
    result = await db.execute(select(Employee).where(Employee.id == employee_id))
    employee = result.scalar_one_or_none()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {employee_id} not found.",
        )

    return EmployeeResponse.model_validate(employee)



async def create_employee_service(
    db: AsyncSession,
    data: EmployeeCreate,
) -> EmployeeResponse:
    """
    Creates a new employee record in the tenant's isolated schema.
    If a PIN is provided it is hashed before storage.
    """
    pin_hash = hash_password(data.pin) if data.pin else None
    new_employee = Employee(
        name=data.name,
        date_of_birth=data.date_of_birth,
        phone=data.phone,
        pin_hash=pin_hash,
    )
    db.add(new_employee)

    try:
        await db.flush()
        await db.refresh(new_employee)
        return EmployeeResponse(
            id=new_employee.id,
            name=new_employee.name,
            date_of_birth=new_employee.date_of_birth,
            phone=new_employee.phone,
            created_at=new_employee.created_at,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create employee: {str(e)}",
        )


async def update_employee_service(
    db: AsyncSession,
    employee_id: int,
    data: EmployeeUpdate,
) -> EmployeeResponse:
    """
    Updates an existing employee record in the tenant's isolated schema.
    """
    result = await db.execute(select(Employee).where(Employee.id == employee_id))
    employee = result.scalar_one_or_none()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {employee_id} not found.",
        )

    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        return EmployeeResponse(
            id=employee.id,
            name=employee.name,
            date_of_birth=employee.date_of_birth,
            phone=employee.phone,
            created_at=employee.created_at,
        )

    # Handle PIN separately — hash it before storing
    if "pin" in update_data:
        raw_pin = update_data.pop("pin")
        update_data["pin_hash"] = hash_password(raw_pin) if raw_pin else None

    for field, value in update_data.items():
        setattr(employee, field, value)

    try:
        await db.flush()
        await db.refresh(employee)
        return EmployeeResponse(
            id=employee.id,
            name=employee.name,
            date_of_birth=employee.date_of_birth,
            phone=employee.phone,
            created_at=employee.created_at,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update employee: {str(e)}",
        )


async def delete_employee_service(
    db: AsyncSession,
    employee_id: int,
) -> EmployeeDeleteResponse:
    """
    Deletes an employee record from the tenant's isolated schema.
    """
    result = await db.execute(select(Employee).where(Employee.id == employee_id))
    employee = result.scalar_one_or_none()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {employee_id} not found.",
        )

    try:
        await db.delete(employee)
        await db.flush()
        return EmployeeDeleteResponse(
            message=f"Employee {employee_id} deleted successfully.",
            employee_id=employee_id,
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete employee {employee_id} because associated active records (such as shifts or orders) exist.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete employee: {str(e)}",
        )
