from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.cloud.auth.dependencies import require_schema_owner, get_scoped_db
from app.models.report_schemas import (
    SalesReportResponse,
    InventoryReportResponse,
    ShiftReportResponse,
    AuditLogResponse,
)
from app.services.report_service import (
    get_sales_report_service,
    get_inventory_report_service,
    get_shift_report_service,
)
from app.services.audit_service import get_audit_logs_service

router = APIRouter(prefix="/cloud/reports", tags=["Cloud Reports & Auditing"])


@router.get("/sales", response_model=SalesReportResponse)
async def get_sales_report(
    branch_id: Optional[int] = Query(None, description="Filter by branch ID"),
    employee_id: Optional[int] = Query(None, description="Filter by employee ID"),
    start_date: Optional[datetime] = Query(None, description="Filter start date (ISO string)"),
    end_date: Optional[datetime] = Query(None, description="Filter end date (ISO string)"),
    current_user: dict = Depends(require_schema_owner),
    db: AsyncSession = Depends(get_scoped_db),
):
    """
    Generates an aggregated sales report with totals, refunded sales, average order value,
    and branch / employee sales breakdowns.
    """
    return await get_sales_report_service(
        db=db,
        branch_id=branch_id,
        employee_id=employee_id,
        start_date=start_date,
        end_date=end_date,
    )


@router.get("/inventory", response_model=InventoryReportResponse)
async def get_inventory_report(
    low_stock_only: bool = Query(False, description="Filter items at or below minimum stock threshold"),
    current_user: dict = Depends(require_schema_owner),
    db: AsyncSession = Depends(get_scoped_db),
):
    """
    Generates a warehouse inventory stock report flagging items at or below minimum stock thresholds.
    """
    return await get_inventory_report_service(db=db, low_stock_only=low_stock_only)


@router.get("/shifts", response_model=ShiftReportResponse)
async def get_shift_report(
    branch_id: Optional[int] = Query(None, description="Filter by branch ID"),
    employee_id: Optional[int] = Query(None, description="Filter by employee ID"),
    start_date: Optional[datetime] = Query(None, description="Filter start date"),
    end_date: Optional[datetime] = Query(None, description="Filter end date"),
    current_user: dict = Depends(require_schema_owner),
    db: AsyncSession = Depends(get_scoped_db),
):
    """
    Generates a shift reconciliation report detailing opening/closing cash, sales totals, pay-in/pay-out drawer counts, and cash variance.
    """
    return await get_shift_report_service(
        db=db,
        branch_id=branch_id,
        employee_id=employee_id,
        start_date=start_date,
        end_date=end_date,
    )


@router.get("/audit-logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    table_name: Optional[str] = Query(None, description="Filter by table name"),
    employee_id: Optional[int] = Query(None, description="Filter by employee ID"),
    action: Optional[str] = Query(None, description="Filter by action type ('INSERT', 'UPDATE', 'DELETE')"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: dict = Depends(require_schema_owner),
    db: AsyncSession = Depends(get_scoped_db),
):
    """
    Retrieves the tenant's structured audit log history for database table mutations.
    """
    return await get_audit_logs_service(
        db=db,
        table_name=table_name,
        employee_id=employee_id,
        action=action,
        skip=skip,
        limit=limit,
    )
