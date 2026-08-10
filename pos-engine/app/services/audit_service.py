from typing import List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.db.models.tenant_models import AuditLog, Employee
from app.models.report_schemas import AuditLogResponse


async def log_audit_event_service(
    db: AsyncSession,
    table_name: str,
    record_id: int,
    action: str,  # 'INSERT', 'UPDATE', 'DELETE'
    employee_id: Optional[int] = None,
    old_value: Optional[Any] = None,
    new_value: Optional[Any] = None,
) -> AuditLog:
    """
    Inserts a structured mutation event log entry into the tenant's audit_logs table.
    """
    log_entry = AuditLog(
        employee_id=employee_id,
        table_name=table_name,
        record_id=record_id,
        action=action.upper(),
        old_value=old_value,
        new_value=new_value,
    )
    db.add(log_entry)
    try:
        await db.flush()
        return log_entry
    except Exception as e:
        # Audit logging should not crash business transactions, log internally if error occurs
        print(f"Warning: Audit log insertion failed: {str(e)}")
        return log_entry


async def get_audit_logs_service(
    db: AsyncSession,
    table_name: Optional[str] = None,
    employee_id: Optional[int] = None,
    action: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[AuditLogResponse]:
    """
    Queries audit log history with optional filters on table_name, employee_id, or action type.
    """
    conditions = []
    if table_name:
        conditions.append(AuditLog.table_name == table_name)
    if employee_id:
        conditions.append(AuditLog.employee_id == employee_id)
    if action:
        conditions.append(AuditLog.action == action.upper())

    query = (
        select(
            AuditLog.id,
            AuditLog.employee_id,
            Employee.name.label("employee_name"),
            AuditLog.table_name,
            AuditLog.record_id,
            AuditLog.action,
            AuditLog.old_value,
            AuditLog.new_value,
            AuditLog.created_at,
        )
        .outerjoin(Employee, AuditLog.employee_id == Employee.id)
        .where(*conditions)
        .order_by(AuditLog.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(query)
    rows = result.all()

    return [
        AuditLogResponse(
            id=r[0],
            employee_id=r[1],
            employee_name=r[2],
            table_name=r[3],
            record_id=r[4],
            action=r[5],
            old_value=r[6],
            new_value=r[7],
            created_at=r[8],
        )
        for r in rows
    ]
