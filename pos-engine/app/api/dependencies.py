from fastapi import Depends, HTTPException, status
from sqlalchemy import text
from app.api.cloud.auth.dependencies import get_current_tenant_user, require_schema_owner, oauth2_scheme
from app.db.database import AsyncSessionLocal

__all__ = [
    "get_current_tenant_user",
    "require_schema_owner",
    "oauth2_scheme",
    "get_current_employee",
    "get_pos_conn",
    "require_permission",
]


async def get_current_employee(current_user: dict = Depends(get_current_tenant_user)) -> dict:
    if "employee_id" not in current_user or "branch_id" not in current_user:
        # Fallback defaults for dev testing if tenant user is logged in
        current_user.setdefault("employee_id", 1)
        current_user.setdefault("branch_id", 1)
    return current_user


async def get_pos_conn(current_user: dict = Depends(get_current_tenant_user)):
    schema_name = current_user.get("schema_name", "public")
    async with AsyncSessionLocal() as session:
        await session.execute(text(f"SET search_path TO {schema_name}"))
        connection = await session.connection()
        raw_conn = await connection.get_raw_connection()
        yield raw_conn.driver_connection


def require_permission(permission_code: str):
    async def permission_checker(current_user: dict = Depends(get_current_tenant_user)):
        permissions = current_user.get("permissions", [])
        role = current_user.get("role")
        if permission_code not in permissions and "ALL" not in permissions and role not in ["TENANT_OWNER", "SUPER_ADMIN"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission_code}' required",
            )
        return await get_current_employee(current_user)
    return permission_checker

