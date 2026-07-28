from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from app.core.security import SECRET_KEY, ALGORITHM
from app.db.database import get_db_connection
import asyncpg

# Tells FastAPI where the login URL is for Swagger UI testing
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_tenant_user(
    token: str = Depends(oauth2_scheme),
    conn: asyncpg.Connection = Depends(get_db_connection),
):
    try:
        # 1. Decode the token cryptographically
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        schema_name = payload.get("schema_name")

        if not schema_name:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing routing payload")

        # 2. DYNAMIC ROUTING: Lock this database connection to the tenant's schema
        # This protects against cross-tenant data leaks
        await conn.execute(f"SET search_path TO {schema_name};")

        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token")
