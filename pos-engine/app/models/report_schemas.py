from pydantic import BaseModel, Field
from typing import List, Optional, Any
from decimal import Decimal
from datetime import datetime


# --- Sales Report Schemas ---

class BranchSalesBreakdown(BaseModel):
    branch_id: int
    branch_name: str
    sales_amount: Decimal
    orders_count: int


class EmployeeSalesBreakdown(BaseModel):
    employee_id: int
    employee_name: str
    sales_amount: Decimal
    orders_count: int


class SalesReportResponse(BaseModel):
    total_sales_amount: Decimal
    total_orders_count: int
    total_refunded_amount: Decimal
    refunded_orders_count: int
    average_order_value: Decimal
    by_branch: List[BranchSalesBreakdown] = []
    by_employee: List[EmployeeSalesBreakdown] = []


# --- Inventory Report Schemas ---

class InventoryReportItem(BaseModel):
    warehouse_item_id: int
    name: str
    sku: Optional[str] = None
    unit_of_measure: str
    minimum_stock: Decimal
    current_stock: Decimal
    is_low_stock: bool


class InventoryReportResponse(BaseModel):
    total_warehouse_items: int
    low_stock_items_count: int
    items: List[InventoryReportItem] = []


# --- Shift Report Schemas ---

class ShiftReportItem(BaseModel):
    shift_id: int
    employee_id: int
    employee_name: str
    branch_id: int
    branch_name: str
    opened_at: datetime
    closed_at: Optional[datetime] = None
    opening_cash: Decimal
    closing_cash: Optional[Decimal] = None
    total_sales_amount: Decimal
    total_cash_sales_amount: Decimal
    total_pay_in_amount: Decimal
    total_pay_out_amount: Decimal
    expected_drawer_cash: Decimal
    cash_variance: Optional[Decimal] = None  # closing_cash - expected_drawer_cash


class ShiftReportResponse(BaseModel):
    total_shifts_count: int
    total_sales_amount: Decimal
    total_cash_sales_amount: Decimal
    total_variance_amount: Decimal
    shifts: List[ShiftReportItem] = []


# --- Audit Log Schemas ---

class AuditLogResponse(BaseModel):
    id: int
    employee_id: Optional[int] = None
    employee_name: Optional[str] = None
    table_name: str
    record_id: int
    action: str
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    created_at: datetime

    class Config:
        from_attributes = True
