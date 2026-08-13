from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_db
from app.db.models.cloud_models import Tenant, User
from app.models.auth_schemas import CurrentUserResponse
from app.api.cloud.auth.dependencies import get_current_tenant_user

router = APIRouter()


@router.get("/me", response_model=CurrentUserResponse)
async def read_current_user(
    current_user: dict = Depends(get_current_tenant_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Session bootstrap. Validates the bearer token and re-reads the user from the
    database so the frontend never has to trust values it decoded client-side.
    """
    user_id = current_user.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user identity",
        )

    result = await db.execute(
        select(
            User.id,
            User.email,
            User.role,
            User.tenant_id,
            Tenant.schema_name,
            Tenant.name.label("tenant_name"),
            Tenant.state,
        )
        .join(Tenant, User.tenant_id == Tenant.id)
        .where(User.id == user_id)
    )
    row = result.first()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists",
        )

    # A tenant can be deactivated after a token was issued - re-check every time.
    if row.state != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Payment not completed. Please finish checkout to activate your account.",
        )

    return CurrentUserResponse(
        id=row.id,
        email=row.email,
        role=str(row.role.value if hasattr(row.role, "value") else row.role),
        tenant_id=row.tenant_id,
        schema_name=row.schema_name,
        tenant_name=row.tenant_name,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout():
    """
    JWTs are stateless, so there is no server-side session to destroy. This exists
    so the client has a well-defined endpoint to call, and as the hook point for
    token revocation/denylisting if that is added later.
    """
    return None
