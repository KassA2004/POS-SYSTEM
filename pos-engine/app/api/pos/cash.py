from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.cloud.auth.dependencies import get_scoped_db
from app.api.dependencies import get_current_employee
from app.models.cash_schemas import CashPayInRequest, CashPayOutRequest, CashTransactionResponse
from app.services.cash_service import cash_pay_in_service, cash_pay_out_service

router = APIRouter(prefix="/pos/cash", tags=["POS Cash Operations"])


@router.post("/pay-in", response_model=CashTransactionResponse, status_code=status.HTTP_201_CREATED)
async def cash_pay_in(
    request: CashPayInRequest,
    current_employee: dict = Depends(get_current_employee),
    db: AsyncSession = Depends(get_scoped_db),
):
    """
    Records a manual cash addition (PAY_IN) to the drawer for the authenticated employee's active shift.

    - Verifies the referenced shift is open and belongs to this employee.
    - Inserts a PAY_IN record into `cash_transactions`.
    - The `expected_drawer_cash` in the shift summary will include this amount.
    """
    employee_id = current_employee["employee_id"]
    return await cash_pay_in_service(db, employee_id, request)


@router.post("/pay-out", response_model=CashTransactionResponse, status_code=status.HTTP_201_CREATED)
async def cash_pay_out(
    request: CashPayOutRequest,
    current_employee: dict = Depends(get_current_employee),
    db: AsyncSession = Depends(get_scoped_db),
):
    """
    Records a manual cash removal (PAY_OUT) from the drawer for the authenticated employee's active shift.

    - Verifies the referenced shift is open and belongs to this employee.
    - Inserts a PAY_OUT record into `cash_transactions`.
    - The `expected_drawer_cash` in the shift summary will deduct this amount.
    """
    employee_id = current_employee["employee_id"]
    return await cash_pay_out_service(db, employee_id, request)
