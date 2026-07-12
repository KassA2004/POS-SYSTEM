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
        print(f"✅ Successfully provisioned tables for schema: {schema_name}")

        # Reset the search path back to public for safety
        await conn.execute("SET search_path TO public;")

    except Exception as e:
        print(f"❌ Failed to provision schema {schema_name}: {e}")
        raise e