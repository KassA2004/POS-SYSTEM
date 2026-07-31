from fastapi import APIRouter, Depends, status
import asyncpg
from app.db.database import get_db_connection
from app.api.cloud.auth.dependencies import require_schema_owner
from app.models.employee_schemas import EmployeeCreate, EmployeeUpdate, EmployeeResponse, EmployeeDeleteResponse
from app.services.employee_service import (
    create_employee_service,
    update_employee_service,
    delete_employee_service,
)

router = APIRouter(prefix="/employees", tags=["Cloud Employee Management"])


@router.post("/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(
    data: EmployeeCreate,
    current_user: dict = Depends(require_schema_owner),
    conn: asyncpg.Connection = Depends(get_db_connection),
):
    """
    Creates a new employee record in the tenant's isolated schema.
    """
    return await create_employee_service(conn, data)


@router.put("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: int,
    data: EmployeeUpdate,
    current_user: dict = Depends(require_schema_owner),
    conn: asyncpg.Connection = Depends(get_db_connection),
):
    """
    Updates an employee record by ID in the tenant's isolated schema.
    """
    return await update_employee_service(conn, employee_id, data)


@router.delete("/{employee_id}", response_model=EmployeeDeleteResponse)
async def delete_employee(
    employee_id: int,
    current_user: dict = Depends(require_schema_owner),
    conn: asyncpg.Connection = Depends(get_db_connection),
):
    """
    Deletes an employee record by ID from the tenant's isolated schema.
    """
    return await delete_employee_service(conn, employee_id)
