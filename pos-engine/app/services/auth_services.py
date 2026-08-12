from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from fastapi import HTTPException, status
from app.db.models.cloud_models import Tenant, User, CloudRole
from app.models.auth_schemas import TenantRegistrationRequest, TenantRegistrationResponse, Token
from app.core.security import hash_password, verify_password, create_access_token
from app.services.stripe_service import create_checkout_session


async def register_tenant_service(
    db: AsyncSession,
    request: TenantRegistrationRequest,
) -> TenantRegistrationResponse:
    """
    Registers a new tenant and owner user, initiates a Stripe checkout session,
    and returns registration response details.
    """
    clean_schema_name = "schema_" + request.company_name.lower().replace(" ", "_").replace("-", "_")
    hashed_pw = hash_password(request.password)

    try:
        # 1. Insert tenant with state = 0 (pending payment)
        new_tenant = Tenant(
            name=request.company_name,
            schema_name=clean_schema_name,
            state=0,
        )
        db.add(new_tenant)
        await db.flush()  # writes row + generates id without committing

        # 2. Insert tenant owner user
        new_user = User(
            tenant_id=new_tenant.id,
            email=request.email,
            password_hash=hashed_pw,
            role=CloudRole.TENANT_OWNER,
        )
        db.add(new_user)
        await db.flush()

        # 3. Create Stripe Checkout Session
        stripe_session = create_checkout_session(
            tenant_id=new_tenant.id,
            company_name=request.company_name,
            email=request.email,
        )
        session_id = stripe_session["session_id"]
        checkout_url = stripe_session["checkout_url"]

        # 4. Store payment_session_id on tenant row
        await db.execute(
            update(Tenant)
            .where(Tenant.id == new_tenant.id)
            .values(payment_session_id=session_id)
        )

        return TenantRegistrationResponse(
            tenant_id=new_tenant.id,
            company_name=request.company_name,
            schema_name=clean_schema_name,
            state=0,
            checkout_url=checkout_url,
            session_id=session_id,
            message="Registration pending payment. Please complete payment via Stripe to activate tenant schema.",
        )

    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        if "unique" in error_msg.lower() or "duplicate" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This email or business name is already registered.",
            )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_msg)


async def authenticate_user_service(
    db: AsyncSession,
    email: str,
    password: str,
) -> Token:
    """
    Authenticates user credentials against DB and generates JWT token with tenant routing payload.
    """
    result = await db.execute(
        select(
            User.id.label("user_id"),
            User.tenant_id,
            User.email,
            User.password_hash,
            User.role,
            Tenant.schema_name,
            Tenant.state.label("tenant_state"),
        )
        .join(Tenant, User.tenant_id == Tenant.id)
        .where(User.email == email)
    )
    row = result.first()

    if not row or not verify_password(password, row.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if row.tenant_state != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Payment not completed. Please finish checkout to activate your account.",
        )

    token_data = {
        "sub": str(row.user_id),
        "user_id": row.user_id,
        "email": row.email,
        "tenant_id": row.tenant_id,
        "schema_name": row.schema_name,
        "role": str(row.role),
    }

    access_token = create_access_token(data=token_data)
    return Token(access_token=access_token, token_type="bearer")
