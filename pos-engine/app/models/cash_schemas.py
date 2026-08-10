from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime


class CashPayInRequest(BaseModel):
    shift_id: int = Field(..., description="The active shift ID for this cash operation")
    amount: Decimal = Field(..., gt=Decimal("0.00"), description="Amount to add to drawer")
    reason: Optional[str] = Field(None, description="Optional reason / note for this pay-in")


class CashPayOutRequest(BaseModel):
    shift_id: int = Field(..., description="The active shift ID for this cash operation")
    amount: Decimal = Field(..., gt=Decimal("0.00"), description="Amount to remove from drawer")
    reason: Optional[str] = Field(None, description="Optional reason / note for this pay-out")


class CashTransactionResponse(BaseModel):
    id: int
    shift_id: int
    employee_id: int
    amount: Decimal
    transaction_type: str  # 'PAY_IN' | 'PAY_OUT'
    reason: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
