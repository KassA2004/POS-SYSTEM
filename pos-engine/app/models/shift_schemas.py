from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime


class ShiftOpenRequest(BaseModel):
    opening_cash: Decimal = Field(..., ge=Decimal("0.00"), description="Opening cash amount in drawer")


class ShiftCloseRequest(BaseModel):
    closing_cash: Decimal = Field(..., ge=Decimal("0.00"), description="Closing cash amount in drawer")


class ShiftResponse(BaseModel):
    id: int
    employee_id: int
    branch_id: int
    opened_at: datetime
    closed_at: Optional[datetime] = None
    opening_cash: Decimal
    closing_cash: Optional[Decimal] = None

    class Config:
        from_attributes = True


class ShiftSummaryResponse(BaseModel):
    shift_id: int
    employee_name: str
    branch_name: str
    opened_at: datetime
    closed_at: Optional[datetime] = None
    opening_cash: Decimal
    closing_cash: Optional[Decimal] = None
    total_sales_amount: Decimal
    sales_order_count: int
    total_pay_in_amount: Decimal
    total_pay_out_amount: Decimal
    expected_drawer_cash: Decimal

    class Config:
        from_attributes = True
