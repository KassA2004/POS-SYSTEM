from pydantic import BaseModel, Field
from typing import List, Optional
from decimal import Decimal
from datetime import datetime


class OrderLineItemCreate(BaseModel):
    product_id: int = Field(..., description="ID of the product being purchased")
    quantity: int = Field(..., gt=0, description="Quantity of product (must be greater than 0)")


class PaymentCreate(BaseModel):
    amount: Decimal = Field(..., gt=Decimal("0.00"), description="Payment amount")
    payment_method: str = Field(..., min_length=1, max_length=50, description="Payment method (e.g., 'cash', 'card')")
    reference_number: Optional[str] = Field(None, max_length=255, description="Optional payment reference transaction ID")


class OrderCreateRequest(BaseModel):
    order_number: Optional[str] = Field(None, max_length=100, description="Unique order number (auto-generated if omitted)")
    line_items: List[OrderLineItemCreate] = Field(..., min_length=1, description="List of items in the order")
    payment: PaymentCreate = Field(..., description="Payment details for the order")


class OrderUpdateRequest(BaseModel):
    status: str = Field(..., description="New order status (must be 'voided' or 'refunded')")
    reason: Optional[str] = Field(None, description="Optional reason for voiding or refunding order")


class OrderLineItemResponse(BaseModel):
    id: int
    order_id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    subtotal_price: Decimal

    class Config:
        from_attributes = True


class PaymentResponse(BaseModel):
    id: int
    order_id: int
    amount: Decimal
    payment_method: str
    status: str
    reference_number: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    branch_id: int
    employee_id: int
    order_number: str
    status: str
    total_amount: Decimal
    created_at: datetime
    updated_at: datetime
    line_items: List[OrderLineItemResponse] = []
    payments: List[PaymentResponse] = []

    class Config:
        from_attributes = True
