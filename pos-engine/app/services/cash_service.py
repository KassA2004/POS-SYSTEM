from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.db.models.tenant_models import CashTransaction, Shift
from app.models.cash_schemas import CashPayInRequest, CashPayOutRequest, CashTransactionResponse


async def _verify_active_shift(db: AsyncSession, shift_id: int, employee_id: int) -> Shift:
    """
    Confirms the shift exists, is owned by the employee, and is still open.
    Raises 404 or 400 if not found / already closed.
    """
    result = await db.execute(
        select(Shift).where(
            Shift.id == shift_id,
            Shift.employee_id == employee_id,
            Shift.closed_at.is_(None),
        )
    )
    shift = result.scalar_one_or_none()
    if not shift:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No open shift with ID {shift_id} found for this employee.",
        )
    return shift


async def cash_pay_in_service(
    db: AsyncSession,
    employee_id: int,
    data: CashPayInRequest,
) -> CashTransactionResponse:
    """
    Records a manual PAY_IN (cash addition to drawer) for an active shift.
    """
    await _verify_active_shift(db, data.shift_id, employee_id)

    tx = CashTransaction(
        shift_id=data.shift_id,
        employee_id=employee_id,
        amount=data.amount,
        transaction_type="PAY_IN",
        reason=data.reason,
    )
    db.add(tx)

    try:
        await db.flush()
        await db.refresh(tx)
        return CashTransactionResponse.model_validate(tx)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record pay-in: {str(e)}",
        )


async def cash_pay_out_service(
    db: AsyncSession,
    employee_id: int,
    data: CashPayOutRequest,
) -> CashTransactionResponse:
    """
    Records a manual PAY_OUT (cash removal from drawer) for an active shift.
    """
    await _verify_active_shift(db, data.shift_id, employee_id)

    tx = CashTransaction(
        shift_id=data.shift_id,
        employee_id=employee_id,
        amount=data.amount,
        transaction_type="PAY_OUT",
        reason=data.reason,
    )
    db.add(tx)

    try:
        await db.flush()
        await db.refresh(tx)
        return CashTransactionResponse.model_validate(tx)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record pay-out: {str(e)}",
        )
