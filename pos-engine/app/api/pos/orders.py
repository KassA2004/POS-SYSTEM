from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.cloud.auth.dependencies import get_scoped_db
from app.api.dependencies import get_current_employee
from app.models.order_schemas import (
    OrderCreateRequest,
    OrderUpdateRequest,
    OrderResponse,
)
from app.services.order_service import (
    create_order_service,
    update_order_status_service,
    get_orders_service,
    get_order_by_id_service,
)

router = APIRouter(prefix="/pos/orders", tags=["POS Order Management"])


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    request: OrderCreateRequest,
    current_employee: dict = Depends(get_current_employee),
    db: AsyncSession = Depends(get_scoped_db),
):
    """
    Creates a new POS order, line items, and payment atomically.

    - Resolves product prices and dynamic recipe / direct warehouse item requirements.
    - Locks warehouse inventory rows (`FOR UPDATE`) to verify stock availability.
    - Atomically deducts inventory stock and logs transaction entries in `inventory_transactions`.
    - Saves order, line items, and payment in a single atomic transaction.
    """
    employee_id = current_employee["employee_id"]
    branch_id = current_employee["branch_id"]
    return await create_order_service(db, employee_id, branch_id, request)


@router.put("/{order_id}", response_model=OrderResponse)
async def update_order_status(
    order_id: int,
    request: OrderUpdateRequest,
    current_employee: dict = Depends(get_current_employee),
    db: AsyncSession = Depends(get_scoped_db),
):
    """
    Processes an Order Void or Refund (`status` = 'voided' or 'refunded').

    - Verifies order exists and is in active paid state.
    - Restores inventory quantities for recipe ingredients or direct warehouse items.
    - Logs inverse movement entries (`transaction_type` = 'RETURN') in `inventory_transactions`.
    - Updates order and payment status.
    """
    employee_id = current_employee["employee_id"]
    branch_id = current_employee["branch_id"]
    return await update_order_status_service(db, employee_id, branch_id, order_id, request)


@router.get("/", response_model=List[OrderResponse])
async def get_orders(
    skip: int = 0,
    limit: int = 100,
    current_employee: dict = Depends(get_current_employee),
    db: AsyncSession = Depends(get_scoped_db),
):
    """
    Retrieves order history for the current employee's branch.
    """
    branch_id = current_employee["branch_id"]
    return await get_orders_service(db, branch_id, skip=skip, limit=limit)


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_by_id(
    order_id: int,
    current_employee: dict = Depends(get_current_employee),
    db: AsyncSession = Depends(get_scoped_db),
):
    """
    Retrieves full details for a single order including line items and payment history.
    """
    branch_id = current_employee["branch_id"]
    return await get_order_by_id_service(db, branch_id, order_id)
