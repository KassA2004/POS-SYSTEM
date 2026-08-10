from typing import List, Optional
from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case, or_

from app.db.models.tenant_models import (
    Order,
    Payment,
    WarehouseItem,
    InventoryWarehouse,
    Shift,
    CashTransaction,
    Branch,
    Employee,
)
from app.models.report_schemas import (
    SalesReportResponse,
    BranchSalesBreakdown,
    EmployeeSalesBreakdown,
    InventoryReportResponse,
    InventoryReportItem,
    ShiftReportResponse,
    ShiftReportItem,
)


async def get_sales_report_service(
    db: AsyncSession,
    branch_id: Optional[int] = None,
    employee_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> SalesReportResponse:
    """
    Generates an aggregated sales report with totals, refunds, average order value,
    and branch/employee breakdowns.
    """
    # 1. Base conditions
    conditions = []
    if branch_id is not None:
        conditions.append(Order.branch_id == branch_id)
    if employee_id is not None:
        conditions.append(Order.employee_id == employee_id)
    if start_date is not None:
        conditions.append(Order.created_at >= start_date)
    if end_date is not None:
        conditions.append(Order.created_at <= end_date)

    # 2. Query paid / closed sales
    paid_conditions = list(conditions) + [Order.status.in_(["paid", "closed"])]
    paid_query = select(
        func.coalesce(func.sum(Order.total_amount), Decimal("0.00")),
        func.count(Order.id),
    ).where(*paid_conditions)

    paid_res = await db.execute(paid_query)
    total_sales_amount, total_orders_count = paid_res.first()

    # 3. Query refunded / voided sales
    refund_conditions = list(conditions) + [Order.status.in_(["refunded", "voided"])]
    refund_query = select(
        func.coalesce(func.sum(Order.total_amount), Decimal("0.00")),
        func.count(Order.id),
    ).where(*refund_conditions)

    refund_res = await db.execute(refund_query)
    total_refunded_amount, refunded_orders_count = refund_res.first()

    avg_order_val = Decimal("0.00")
    if total_orders_count > 0:
        avg_order_val = (total_sales_amount / Decimal(total_orders_count)).round(2)

    # 4. Branch sales breakdown
    branch_query = (
        select(
            Branch.id,
            Branch.name,
            func.coalesce(func.sum(Order.total_amount), Decimal("0.00")),
            func.count(Order.id),
        )
        .join(Order, Branch.id == Order.branch_id)
        .where(*paid_conditions)
        .group_by(Branch.id, Branch.name)
    )
    branch_res = await db.execute(branch_query)
    by_branch = [
        BranchSalesBreakdown(
            branch_id=row[0],
            branch_name=row[1],
            sales_amount=row[2],
            orders_count=row[3],
        )
        for row in branch_res.all()
    ]

    # 5. Employee sales breakdown
    emp_query = (
        select(
            Employee.id,
            Employee.name,
            func.coalesce(func.sum(Order.total_amount), Decimal("0.00")),
            func.count(Order.id),
        )
        .join(Order, Employee.id == Order.employee_id)
        .where(*paid_conditions)
        .group_by(Employee.id, Employee.name)
    )
    emp_res = await db.execute(emp_query)
    by_employee = [
        EmployeeSalesBreakdown(
            employee_id=row[0],
            employee_name=row[1],
            sales_amount=row[2],
            orders_count=row[3],
        )
        for row in emp_res.all()
    ]

    return SalesReportResponse(
        total_sales_amount=total_sales_amount,
        total_orders_count=total_orders_count,
        total_refunded_amount=total_refunded_amount,
        refunded_orders_count=refunded_orders_count,
        average_order_value=avg_order_val,
        by_branch=by_branch,
        by_employee=by_employee,
    )


async def get_inventory_report_service(
    db: AsyncSession,
    low_stock_only: bool = False,
) -> InventoryReportResponse:
    """
    Generates a warehouse inventory stock report, flagging stock levels below minimum stock threshold.
    """
    query = (
        select(
            WarehouseItem.id,
            WarehouseItem.name,
            WarehouseItem.sku,
            WarehouseItem.unit_of_measure,
            WarehouseItem.minimum_stock,
            func.coalesce(InventoryWarehouse.quantity, Decimal("0.000")).label("current_stock"),
        )
        .outerjoin(InventoryWarehouse, WarehouseItem.id == InventoryWarehouse.warehouse_item_id)
        .order_by(WarehouseItem.id.asc())
    )

    result = await db.execute(query)
    rows = result.all()

    items = []
    low_stock_count = 0

    for row in rows:
        w_id, name, sku, uom, min_stock, curr_stock = row
        is_low = curr_stock <= min_stock
        if is_low:
            low_stock_count += 1

        if low_stock_only and not is_low:
            continue

        items.append(
            InventoryReportItem(
                warehouse_item_id=w_id,
                name=name,
                sku=sku,
                unit_of_measure=uom,
                minimum_stock=min_stock,
                current_stock=curr_stock,
                is_low_stock=is_low,
            )
        )

    return InventoryReportResponse(
        total_warehouse_items=len(rows),
        low_stock_items_count=low_stock_count,
        items=items,
    )


async def get_shift_report_service(
    db: AsyncSession,
    branch_id: Optional[int] = None,
    employee_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> ShiftReportResponse:
    """
    Generates a shift reconciliation report detailing sales, drawer movements, expected cash, and variance.
    """
    conditions = []
    if branch_id is not None:
        conditions.append(Shift.branch_id == branch_id)
    if employee_id is not None:
        conditions.append(Shift.employee_id == employee_id)
    if start_date is not None:
        conditions.append(Shift.opened_at >= start_date)
    if end_date is not None:
        conditions.append(Shift.opened_at <= end_date)

    shift_query = (
        select(
            Shift,
            Employee.name.label("employee_name"),
            Branch.name.label("branch_name"),
        )
        .join(Employee, Shift.employee_id == Employee.id)
        .join(Branch, Shift.branch_id == Branch.id)
        .where(*conditions)
        .order_by(Shift.opened_at.desc())
    )

    result = await db.execute(shift_query)
    shift_rows = result.all()

    shift_items = []
    grand_total_sales = Decimal("0.00")
    grand_cash_sales = Decimal("0.00")
    grand_variance = Decimal("0.00")

    for shift_obj, emp_name, br_name in shift_rows:
        s_opened = shift_obj.opened_at
        s_closed = shift_obj.closed_at or datetime.now(timezone.utc)

        # 1. Sales total for shift
        sales_q = select(
            func.coalesce(func.sum(Order.total_amount), Decimal("0.00"))
        ).where(
            Order.employee_id == shift_obj.employee_id,
            Order.branch_id == shift_obj.branch_id,
            Order.created_at >= s_opened,
            Order.created_at <= s_closed,
            Order.status.in_(["paid", "closed"]),
        )
        tot_sales = (await db.execute(sales_q)).scalar() or Decimal("0.00")

        # 2. Cash sales for shift
        cash_sales_q = select(
            func.coalesce(func.sum(Payment.amount), Decimal("0.00"))
        ).join(Order, Payment.order_id == Order.id).where(
            Order.employee_id == shift_obj.employee_id,
            Order.branch_id == shift_obj.branch_id,
            Order.created_at >= s_opened,
            Order.created_at <= s_closed,
            Payment.payment_method.ilike("cash"),
            Payment.status == "SUCCESS",
        )
        cash_sales = (await db.execute(cash_sales_q)).scalar() or Decimal("0.00")

        # 3. Pay-in / Pay-out cash transactions
        cash_ops_q = select(
            func.coalesce(func.sum(case((CashTransaction.transaction_type == "PAY_IN", CashTransaction.amount), else_=Decimal("0.00"))), Decimal("0.00")),
            func.coalesce(func.sum(case((CashTransaction.transaction_type == "PAY_OUT", CashTransaction.amount), else_=Decimal("0.00"))), Decimal("0.00")),
        ).where(CashTransaction.shift_id == shift_obj.id)
        cash_ops_res = await db.execute(cash_ops_q)
        pay_in, pay_out = cash_ops_res.first()

        expected_cash = shift_obj.opening_cash + cash_sales + pay_in - pay_out
        variance = (shift_obj.closing_cash - expected_cash) if shift_obj.closing_cash is not None else None

        grand_total_sales += tot_sales
        grand_cash_sales += cash_sales
        if variance is not None:
            grand_variance += variance

        shift_items.append(
            ShiftReportItem(
                shift_id=shift_obj.id,
                employee_id=shift_obj.employee_id,
                employee_name=emp_name,
                branch_id=shift_obj.branch_id,
                branch_name=br_name,
                opened_at=shift_obj.opened_at,
                closed_at=shift_obj.closed_at,
                opening_cash=shift_obj.opening_cash,
                closing_cash=shift_obj.closing_cash,
                total_sales_amount=tot_sales,
                total_cash_sales_amount=cash_sales,
                total_pay_in_amount=pay_in,
                total_pay_out_amount=pay_out,
                expected_drawer_cash=expected_cash,
                cash_variance=variance,
            )
        )

    return ShiftReportResponse(
        total_shifts_count=len(shift_items),
        total_sales_amount=grand_total_sales,
        total_cash_sales_amount=grand_cash_sales,
        total_variance_amount=grand_variance,
        shifts=shift_items,
    )
