from fastapi import APIRouter, Depends, HTTPException
from app.models.auth_schemas import TenantRegistrationRequest, TenantRegistrationResponse
from app.db.database import get_db_connection
from app.services.tenant_service import provision_tenant_schema
import asyncpg
import bcrypt

router = APIRouter(prefix="/auth", tags=["Authentication"])


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


@router.post("/register", response_model=TenantRegistrationResponse)
async def register_tenant(
    request: TenantRegistrationRequest,
    conn: asyncpg.Connection = Depends(get_db_connection),
):
    clean_schema_name = "schema_" + request.company_name.lower().replace(" ", "_")

    hashed_pw = hash_password(request.password)

    try:
        tenant_query = """
            INSERT INTO tenants (name, schema_name)
            VALUES ($1, $2)
            RETURNING id;
        """
        tenant_record = await conn.fetchrow(
            tenant_query, request.company_name, clean_schema_name
        )
        new_tenant_id = tenant_record["id"]

        user_query = """
            INSERT INTO users (tenant_id, email, password_hash, role)
            VALUES ($1, $2, $3, 'TENANT_OWNER');
        """
        await conn.execute(user_query, new_tenant_id, request.email, hashed_pw)

        await conn.execute(f"CREATE SCHEMA {clean_schema_name};")
        await provision_tenant_schema(conn, clean_schema_name)

        return TenantRegistrationResponse(
            tenant_id=new_tenant_id,
            company_name=request.company_name,
            schema_name=clean_schema_name,
            message="Registration successful. Isolated database schema created.",
        )

    except asyncpg.exceptions.UniqueViolationError:
        raise HTTPException(
            status_code=400, detail="This email or business name is already registered."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
