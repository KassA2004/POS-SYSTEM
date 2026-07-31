import asyncpg
from fastapi import HTTPException, status
from app.models.auth_schemas import TenantRegistrationRequest, TenantRegistrationResponse, Token
from app.core.security import hash_password, verify_password, create_access_token
from app.services.stripe_service import create_checkout_session


async def register_tenant_service(
    conn: asyncpg.Connection,
    request: TenantRegistrationRequest,
) -> TenantRegistrationResponse:
    """
    Registers a new tenant and owner user, initiates a Stripe checkout session,
    and returns registration response details.
    """
    clean_schema_name = "schema_" + request.company_name.lower().replace(" ", "_").replace("-", "_")
    hashed_pw = hash_password(request.password)

    try:
        # Insert tenant with state = 0 (pending)
        tenant_query = """
            INSERT INTO tenants (name, schema_name, state)
            VALUES ($1, $2, 0)
            RETURNING id;
        """
        tenant_record = await conn.fetchrow(
            tenant_query, request.company_name, clean_schema_name
        )
        new_tenant_id = tenant_record["id"]

        # Insert tenant owner
        user_query = """
            INSERT INTO users (tenant_id, email, password_hash, role)
            VALUES ($1, $2, $3, 'TENANT_OWNER');
        """
        await conn.execute(user_query, new_tenant_id, request.email, hashed_pw)

        # Create Stripe Checkout Session
        stripe_session = create_checkout_session(
            tenant_id=new_tenant_id,
            company_name=request.company_name,
            email=request.email,
        )

        session_id = stripe_session["session_id"]
        checkout_url = stripe_session["checkout_url"]

        # Update tenant record with payment_session_id
        await conn.execute(
            "UPDATE tenants SET payment_session_id = $1 WHERE id = $2;",
            session_id,
            new_tenant_id,
        )

        return TenantRegistrationResponse(
            tenant_id=new_tenant_id,
            company_name=request.company_name,
            schema_name=clean_schema_name,
            state=0,
            checkout_url=checkout_url,
            session_id=session_id,
            message="Registration pending payment. Please complete payment via Stripe to activate tenant schema.",
        )

    except asyncpg.exceptions.UniqueViolationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This email or business name is already registered.",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def authenticate_user_service(
    conn: asyncpg.Connection,
    email: str,
    password: str,
) -> Token:
    """
    Authenticates user credentials against DB and generates JWT token with tenant routing payload.
    """
    user_query = """
        SELECT u.id AS user_id, u.tenant_id, u.email, u.password_hash, u.role, t.schema_name, t.state AS tenant_state
        FROM users u
        JOIN tenants t ON u.tenant_id = t.id
        WHERE u.email = $1;
    """
    user = await conn.fetchrow(user_query, email)

    if not user or not verify_password(password, user["password_hash"]):
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
