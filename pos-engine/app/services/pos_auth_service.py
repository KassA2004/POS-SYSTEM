from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from fastapi import HTTPException, status
from app.db.models.tenant_models import Employee, BranchEmployee, Role, Permission, RolePermission
from app.models.pos_auth_schemas import POSLoginRequest, POSLoginResponse, POSLogoutResponse
from app.core.security import verify_password, create_access_token
from app.db.database import AsyncSessionLocal


async def pos_login_service(login_data: POSLoginRequest) -> POSLoginResponse:
    """
    Authenticates a POS terminal session using Employee numeric ID + PIN.

    Flow:
      1. Open a session scoped to the tenant's isolated schema.
      2. Load employee by ID and verify PIN hash.
      3. Confirm employee has an active assignment at the given branch.
      4. Resolve the employee's role and permissions.
      5. Return a signed JWT with full POS session claims.
    """
    async with AsyncSessionLocal() as session:
        # 1. Scope to tenant schema
        await session.execute(text(f"SET search_path TO {login_data.schema_name}"))

        # 2. Load and verify employee
        emp_result = await session.execute(
            select(Employee).where(Employee.id == login_data.employee_id)
        )
        employee = emp_result.scalar_one_or_none()

        if not employee or not employee.pin_hash:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid employee ID or PIN",
            )

        if not verify_password(login_data.pin, employee.pin_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid employee ID or PIN",
            )

        # 3. Confirm active branch assignment
        assignment_result = await session.execute(
            select(BranchEmployee)
            .where(
                BranchEmployee.employee_id == login_data.employee_id,
                BranchEmployee.branch_id == login_data.branch_id,
                BranchEmployee.removed_at.is_(None),
            )
        )
        assignment = assignment_result.scalar_one_or_none()

        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Employee is not actively assigned to this branch.",
            )

        # 4. Resolve role name and permissions
        role_name: str | None = None
        permission_codes: list[str] = []

        if assignment.role_id:
            role_result = await session.execute(
                select(Role.name).where(Role.id == assignment.role_id)
            )
            role_row = role_result.first()
            if role_row:
                role_name = role_row[0]

            perm_result = await session.execute(
                select(Permission.code)
                .join(RolePermission, Permission.id == RolePermission.permission_id)
                .where(RolePermission.role_id == assignment.role_id)
            )
            permission_codes = [row[0] for row in perm_result.all()]

        # 5. Build and sign JWT
        token_data = {
            "sub": f"employee:{employee.id}",
            "employee_id": employee.id,
            "branch_id": login_data.branch_id,
            "schema_name": login_data.schema_name,
            "role": role_name,
            "permissions": permission_codes,
        }
        access_token = create_access_token(data=token_data)

        return POSLoginResponse(
            access_token=access_token,
            token_type="bearer",
            employee_id=employee.id,
            employee_name=employee.name,
            branch_id=login_data.branch_id,
            role=role_name,
        )


async def pos_logout_service() -> POSLogoutResponse:
    """
    POS terminal logout. JWT is stateless so logout is handled client-side;
    this endpoint exists for audit / UI purposes.
    """
    return POSLogoutResponse(message="POS session terminated successfully.")
