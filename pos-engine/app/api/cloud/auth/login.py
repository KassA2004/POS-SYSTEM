from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
import asyncpg
from app.db.database import get_db_connection
from app.core.security import verify_password, create_access_token
from app.models.auth_schemas import Token

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    conn: asyncpg.Connection = Depends(get_db_connection),
):
    """
    OAuth2 compatible token login.
    Authenticates user with username (email) and password, then returns a JWT token.
    """
    user_query = """
        SELECT u.id AS user_id, u.tenant_id, u.email, u.password_hash, u.role, t.schema_name, t.state AS tenant_state
        FROM users u
        JOIN tenants t ON u.tenant_id = t.id
        WHERE u.email = $1;
    """
    user = await conn.fetchrow(user_query, form_data.username)

    if not user or not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Prepare token payload including routing payload (schema_name)
    token_data = {
        "sub": str(user["user_id"]),
        "user_id": user["user_id"],
        "email": user["email"],
        "tenant_id": user["tenant_id"],
        "schema_name": user["schema_name"],
        "role": str(user["role"]),
    }

    access_token = create_access_token(data=token_data)

    return Token(access_token=access_token, token_type="bearer")
