from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.cloud.auth.dependencies import require_schema_owner, get_scoped_db
from app.models.employee_schemas import EmployeeCreate, EmployeeUpdate, EmployeeResponse, EmployeeDeleteResponse
from app.services.employee_service import (
    create_employee_service,
    get_employees_service,
    get_employee_by_id_service,
    update_employee_service,
    delete_employee_service,
)

router = APIRouter(prefix="/employees", tags=["Cloud Employee Management"])


@router.get("/", response_model=List[EmployeeResponse])
async def get_employees(
    current_user: dict = Depends(require_schema_owner),
    db: AsyncSession = Depends(get_scoped_db),
):
    """
    Retrieves all employee records from the tenant's isolated schema.
    """
    return await get_employees_service(db)


@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee_by_id(
    employee_id: int,
    current_user: dict = Depends(require_schema_owner),
    db: AsyncSession = Depends(get_scoped_db),
):
    """
    Retrieves a single employee record by ID from the tenant's isolated schema.
    """
    return await get_employee_by_id_service(db, employee_id)


@router.post("/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)

async def create_employee(
    data: EmployeeCreate,
    current_user: dict = Depends(require_schema_owner),
    db: AsyncSession = Depends(get_scoped_db),
):
    """
    Creates a new employee record in the tenant's isolated schema.
    """
    return await create_employee_service(db, data)


@router.put("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: int,
    data: EmployeeUpdate,
    current_user: dict = Depends(require_schema_owner),
    db: AsyncSession = Depends(get_scoped_db),
):
    """
    Updates an employee record by ID in the tenant's isolated schema.
    """
    return await update_employee_service(db, employee_id, data)


@router.delete("/{employee_id}", response_model=EmployeeDeleteResponse)
async def delete_employee(
    employee_id: int,
    current_user: dict = Depends(require_schema_owner),
    db: AsyncSession = Depends(get_scoped_db),
):
    """
    Deletes an employee record by ID from the tenant's isolated schema.
    """
    return await delete_employee_service(db, employee_id)
