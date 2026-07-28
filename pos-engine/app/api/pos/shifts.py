from fastapi import APIRouter, Depends, HTTPException, status
import asyncpg
from datetime import datetime, timezone
from decimal import Decimal

from app.models.shift_schemas import ShiftOpenRequest, ShiftCloseRequest, ShiftResponse, ShiftSummaryResponse
from app.api.dependencies import get_current_employee, get_pos_conn, require_permission

router = APIRouter(prefix="/pos/shifts", tags=["POS Shift Management"])

@router.post("/", response_model=ShiftResponse, status_code=status.HTTP_201_CREATED)
async def open_shift(
    request: ShiftOpenRequest,
    current_employee: dict = Depends(get_current_employee),
    conn: asyncpg.Connection = Depends(get_pos_conn)
):
    """Opens a new shift for the authenticated employee at their assigned branch."""
    employee_id = current_employee["employee_id"]
    branch_id = current_employee["branch_id"]
    
    # Check if there is an active shift for this employee at this branch
    active_shift = await conn.fetchrow(
        "SELECT id FROM shifts WHERE employee_id = $1 AND branch_id = $2 AND closed_at IS NULL;",
        employee_id, branch_id
    )
    if active_shift:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An active shift is already open for you at this branch"
        )
        
    query = """
        INSERT INTO shifts (employee_id, branch_id, opening_cash, opened_at)
        VALUES ($1, $2, $3, CURRENT_TIMESTAMP)
        RETURNING id, employee_id, branch_id, opened_at, closed_at, opening_cash, closing_cash;
    """
    row = await conn.fetchrow(query, employee_id, branch_id, request.opening_cash)
    return dict(row)

@router.put("/{shift_id}", response_model=ShiftResponse)
async def close_shift(
    shift_id: int,
    request: ShiftCloseRequest,
    current_employee: dict = Depends(get_current_employee),
    conn: asyncpg.Connection = Depends(get_pos_conn)
):
    """Closes an active shift and timestamps the closure."""
    employee_id = current_employee["employee_id"]
    branch_id = current_employee["branch_id"]
    
    # Find active shift
    shift = await conn.fetchrow(
        "SELECT id FROM shifts WHERE id = $1 AND employee_id = $2 AND branch_id = $3 AND closed_at IS NULL;",
        shift_id, employee_id, branch_id
    )
    if not shift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active shift not found or already closed"
        )
        
    query = """
        UPDATE shifts
        SET closed_at = CURRENT_TIMESTAMP, closing_cash = $1
        WHERE id = $2
        RETURNING id, employee_id, branch_id, opened_at, closed_at, opening_cash, closing_cash;
    """
    row = await conn.fetchrow(query, request.closing_cash, shift_id)
    return dict(row)

@router.get("/{shift_id}/summary", response_model=ShiftSummaryResponse)
async def get_shift_summary(
    shift_id: int,
    current_employee: dict = Depends(require_permission("sales.read_shift")),
    conn: asyncpg.Connection = Depends(get_pos_conn)
):
    """Returns shift metrics for the current shift including sales totals, cash movements, and order count."""
    employee_id = current_employee["employee_id"]
    branch_id = current_employee["branch_id"]
    
    # 1. Fetch shift details
    shift = await conn.fetchrow(
        "SELECT s.id, s.opened_at, s.closed_at, s.opening_cash, s.closing_cash, e.name AS employee_name, b.name AS branch_name "
        "FROM shifts s "
        "JOIN employees e ON s.employee_id = e.id "
        "JOIN branches b ON s.branch_id = b.id "
        "WHERE s.id = $1 AND s.employee_id = $2 AND s.branch_id = $3;",
        shift_id, employee_id, branch_id
    )
    if not shift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shift not found for this employee and branch"
        )
        
    opened_at = shift["opened_at"]
    closed_at = shift["closed_at"] if shift["closed_at"] else datetime.now(timezone.utc)
    
    # 2. Fetch sales summary (paid/closed orders)
    sales_query = """
        SELECT COALESCE(SUM(total_amount), 0) AS total_sales, COUNT(id) AS sales_count
        FROM orders
        WHERE employee_id = $1 AND branch_id = $2
          AND created_at >= $3 AND created_at <= $4
          AND status IN ('paid', 'closed');
    """
    sales_record = await conn.fetchrow(sales_query, employee_id, branch_id, opened_at, closed_at)
    total_sales_amount = sales_record["total_sales"]
    sales_order_count = sales_record["sales_count"]
    
    # 3. Fetch cash payments (portion of sales paid in cash)
    cash_sales_query = """
        SELECT COALESCE(SUM(p.amount), 0) AS cash_payments_total
        FROM payments p
        JOIN orders o ON p.order_id = o.id
        WHERE o.employee_id = $1 AND o.branch_id = $2
          AND o.created_at >= $3 AND o.created_at <= $4
          AND p.payment_method ILIKE 'cash' AND p.status = 'SUCCESS';
    """
    cash_sales_record = await conn.fetchrow(cash_sales_query, employee_id, branch_id, opened_at, closed_at)
    cash_sales_total = cash_sales_record["cash_payments_total"]
    
    # 4. Fetch manual pay-in/pay-out cash operations
    cash_ops_query = """
        SELECT 
            COALESCE(SUM(CASE WHEN transaction_type = 'PAY_IN' THEN amount ELSE 0 END), 0) AS total_pay_in,
            COALESCE(SUM(CASE WHEN transaction_type = 'PAY_OUT' THEN amount ELSE 0 END), 0) AS total_pay_out
        FROM cash_transactions
        WHERE shift_id = $1;
    """
    cash_ops = await conn.fetchrow(cash_ops_query, shift_id)
    total_pay_in = cash_ops["total_pay_in"]
    total_pay_out = cash_ops["total_pay_out"]
    
    # 5. Expected drawer cash: opening_cash + cash_sales + pay_in - pay_out
    expected_drawer_cash = shift["opening_cash"] + cash_sales_total + total_pay_in - total_pay_out
    
    return ShiftSummaryResponse(
        shift_id=shift_id,
        employee_name=shift["employee_name"],
        branch_name=shift["branch_name"],
        opened_at=opened_at,
        closed_at=shift["closed_at"],
        opening_cash=shift["opening_cash"],
        closing_cash=shift["closing_cash"],
        total_sales_amount=total_sales_amount,
        sales_order_count=sales_order_count,
        total_pay_in_amount=total_pay_in,
        total_pay_out_amount=total_pay_out,
        expected_drawer_cash=expected_drawer_cash
    )
