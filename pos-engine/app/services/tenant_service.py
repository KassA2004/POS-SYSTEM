import asyncpg
import os

async def provision_tenant_schema(conn: asyncpg.Connection, schema_name: str):

    current_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    sql_file_path = os.path.join(current_dir, "tenant_schema.sql")

    try:
        with open(sql_file_path, "r") as file:
            schema_sql = file.read()

        # execute SET search_path so the tables are built in the right folder
        await conn.execute(f"SET search_path TO {schema_name};")

        # Run the massive SQL script to build the tables
        await conn.execute(schema_sql)
        
        # Create schema_migrations tracking table and record initial blueprint migration
        await conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {schema_name}.schema_migrations (
                id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                filename VARCHAR(255) UNIQUE NOT NULL,
                applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
            );
        """)
        await conn.execute(
            f"INSERT INTO {schema_name}.schema_migrations (filename) VALUES ($1) ON CONFLICT (filename) DO NOTHING;",
            "001_init_tenant.sql"
        )
        print(f"[Schema] Successfully provisioned tables and migration tracking for schema: {schema_name}")

        # Reset the search path back to public for safety
        await conn.execute("SET search_path TO public;")

    except Exception as e:
        print(f"[Schema Error] Failed to provision schema {schema_name}: {e}")
        raise e


async def activate_tenant_and_create_schema(conn: asyncpg.Connection, tenant_id: int = None, session_id: str = None) -> dict:
    """
    Activates a tenant upon successful payment:
    1. Checks if state is already active (1). If active, returns immediately (idempotent).
    2. Runs CREATE SCHEMA for the tenant.
    3. Runs provision_tenant_schema to populate isolated tenant tables.
    4. Updates tenant state to 1 (active).
    """
    if tenant_id is None and session_id is None:
        raise ValueError("Must provide either tenant_id or session_id")

    if tenant_id:
        tenant = await conn.fetchrow("SELECT id, name, schema_name, state FROM tenants WHERE id = $1;", tenant_id)
    else:
        tenant = await conn.fetchrow("SELECT id, name, schema_name, state FROM tenants WHERE payment_session_id = $1;", session_id)

    if not tenant:
        raise ValueError(f"Tenant not found (tenant_id={tenant_id}, session_id={session_id})")

    # Idempotence check: if state is already 1 (active), schema is already created
    if tenant["state"] == 1:
        print(f"[Tenant Info] Tenant {tenant['id']} ({tenant['schema_name']}) is already active.")
        return dict(tenant)

    schema_name = tenant["schema_name"]

    # 1. Create schema
    await conn.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name};")

    # 2. Provision schema tables
    await provision_tenant_schema(conn, schema_name)

    # 3. Update state to 1 (active)
    await conn.execute("UPDATE tenants SET state = 1 WHERE id = $1;", tenant["id"])
    print(f"[Tenant Success] Tenant {tenant['id']} state updated to 1 (active).")

    return {
        "id": tenant["id"],
        "name": tenant["name"],
        "schema_name": schema_name,
        "state": 1
    }