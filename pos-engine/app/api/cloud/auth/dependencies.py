from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import jwt
from app.core.security import SECRET_KEY, ALGORITHM
from app.db.database import AsyncSessionLocal

# Tells FastAPI where the login URL is for Swagger UI testing
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_tenant_user(
    token: str = Depends(oauth2_scheme),
) -> dict:
    """
    Decodes and validates the JWT. Returns the token payload dict.
    Does NOT yield a DB session — call `get_tenant_db` separately to get a session
    already scoped to this tenant's schema.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        schema_name = payload.get("schema_name")

        if not schema_name:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing routing payload",
            )

        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token")


async def require_schema_owner(
    current_user: dict = Depends(get_current_tenant_user),
) -> dict:
    """
    Dependency that enforces only schema owners (TENANT_OWNER / SUPER_ADMIN)
    can access the endpoint.
    """
    role = current_user.get("role")
    if role not in ["TENANT_OWNER", "SUPER_ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Only schema owners can perform this action.",
        )
    return current_user


async def get_scoped_db(
    current_user: dict = Depends(get_current_tenant_user),
) -> AsyncGenerator[AsyncSession, None]:
    """
    Yields an AsyncSession with search_path already set to the authenticated
    tenant's schema. Use this as the DB dependency on all tenant-scoped routes.

    Example:
        @router.post("/")
        async def create_branch(
            data: BranchCreate,
            current_user: dict = Depends(require_schema_owner),
            db: AsyncSession = Depends(get_scoped_db),
        ):
    """
    schema_name = current_user["schema_name"]
    async with AsyncSessionLocal() as session:
        await session.execute(text(f"SET search_path TO {schema_name}"))
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
