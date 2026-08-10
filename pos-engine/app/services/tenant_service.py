"""
tenant_service.py

Note: Schema provisioning (CREATE SCHEMA, running DDL SQL) cannot be done
through the ORM because it involves DDL statements outside of any tenant schema.
Those operations use raw `text()` executed directly on the session connection.
All other tenant record operations use the SQLAlchemy ORM.
"""
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, text
from app.db.models.cloud_models import Tenant


async def provision_tenant_schema(db: AsyncSession, schema_name: str):
    """
    Runs the tenant_schema.sql DDL inside the given schema.
    Uses raw SQL via text() because this is pure DDL that SQLAlchemy
    doesn't manage through ORM operations.
    """
    current_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    sql_file_path = os.path.join(current_dir, "tenant_schema.sql")

    try:
        with open(sql_file_path, "r") as file:
            schema_sql = file.read()

        # Route this connection to the new tenant schema
        await db.execute(text(f"SET search_path TO {schema_name}"))

        # Run the DDL script to build all tenant tables
        await db.execute(text(schema_sql))

        # Create migration tracking table and record the initial blueprint
        await db.execute(text(f"""
            CREATE TABLE IF NOT EXISTS {schema_name}.schema_migrations (
                id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                filename VARCHAR(255) UNIQUE NOT NULL,
                applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
            );
        """))
        await db.execute(
            text(f"INSERT INTO {schema_name}.schema_migrations (filename) VALUES (:fname) ON CONFLICT (filename) DO NOTHING;"),
            {"fname": "001_init_tenant.sql"},
        )
        print(f"[Schema] Successfully provisioned tables for schema: {schema_name}")

        # Reset search path back to public for safety
        await db.execute(text("SET search_path TO public"))

    except Exception as e:
        print(f"[Schema Error] Failed to provision schema {schema_name}: {e}")
        raise


async def activate_tenant_and_create_schema(
    db: AsyncSession,
    tenant_id: int = None,
    session_id: str = None,
) -> dict:
    """
    Activates a tenant upon successful payment:
    1. Looks up the tenant by tenant_id or Stripe session_id.
    2. Idempotency check — returns immediately if already active.
    3. Runs CREATE SCHEMA for the tenant.
    4. Provisions all tenant tables via tenant_schema.sql.
    5. Updates tenant state to 1 (active).
    """
    if tenant_id is None and session_id is None:
        raise ValueError("Must provide either tenant_id or session_id")

    if tenant_id:
        result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    else:
        result = await db.execute(select(Tenant).where(Tenant.payment_session_id == session_id))

    tenant = result.scalar_one_or_none()

    if not tenant:
        raise ValueError(f"Tenant not found (tenant_id={tenant_id}, session_id={session_id})")

    # Idempotency: already active — nothing to do
    if tenant.state == 1:
        print(f"[Tenant Info] Tenant {tenant.id} ({tenant.schema_name}) is already active.")
        return {"id": tenant.id, "name": tenant.name, "schema_name": tenant.schema_name, "state": 1}

    schema_name = tenant.schema_name

    # 1. Create the PostgreSQL schema
    await db.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))

    # 2. Populate it with all tenant tables
    await provision_tenant_schema(db, schema_name)

    # 3. Mark tenant as active
    await db.execute(
        update(Tenant).where(Tenant.id == tenant.id).values(state=1)
    )
    print(f"[Tenant Success] Tenant {tenant.id} state updated to 1 (active).")

    return {
        "id": tenant.id,
        "name": tenant.name,
        "schema_name": schema_name,
        "state": 1,
    }