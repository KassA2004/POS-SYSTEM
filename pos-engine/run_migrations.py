import asyncio
import asyncpg
from pathlib import Path
import os

# Load .env file if present
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            os.environ.setdefault(key.strip(), val.strip().strip("\"'"))

# Connection string with fallback matching database.py
DB_DSN = os.getenv("DATABASE_URL", "postgresql://postgres:123123@localhost:5432/POS-ENGINE")

async def ensure_migration_table(conn: asyncpg.Connection, schema_name: str):
    """Ensures a tracking table exists in the target schema."""
    await conn.execute(f"""
        CREATE TABLE IF NOT EXISTS {schema_name}.schema_migrations (
            id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            filename VARCHAR(255) UNIQUE NOT NULL,
            applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
        );
    """)

async def apply_migrations_in_folder(conn: asyncpg.Connection, folder_path: str, schema_name: str):
    """Scans a folder for SQL files and applies any that haven't been run."""
    await ensure_migration_table(conn, schema_name)
    
    # Fetch already applied migrations for this specific schema
    applied = await conn.fetch(f"SELECT filename FROM {schema_name}.schema_migrations;")
    applied_files = {record['filename'] for record in applied}
    
    folder = Path(folder_path)
    if not folder.exists():
        print(f"Directory {folder_path} does not exist. Skipping.")
        return

    # Sort files alphabetically to enforce chronological execution (e.g., 001_, 002_)
    sql_files = sorted([f for f in folder.iterdir() if f.suffix == '.sql'])
    
    for file_path in sql_files:
        filename = file_path.name
        if filename not in applied_files:
            print(f" -> Applying {filename} to schema '{schema_name}'...")
            sql_content = file_path.read_text(encoding="utf-8")
            
            # ATOMIC EXECUTION: If a script fails, the schema rolls back completely.
            async with conn.transaction():
                # 1. Lock the PostgreSQL execution scope to this specific schema
                await conn.execute(f"SET search_path TO {schema_name};")
                
                # 2. Run the migration script
                await conn.execute(sql_content)
                
                # 3. Record the migration in the tracking table
                await conn.execute(
                    f"INSERT INTO {schema_name}.schema_migrations (filename) VALUES ($1);", 
                    filename
                )

async def main():
    print("Starting database migrations...")
    conn = await asyncpg.connect(DB_DSN)
    
    try:
        print("\n--- [ Phase 1: Public Routing Layer ] ---")
        await apply_migrations_in_folder(conn, "migrations/public", "public")
        
        print("\n--- [ Phase 2: Isolated Tenant Layers ] ---")
        # Fetch every provisioned schema that has successfully completed checkout
        tenants = await conn.fetch("SELECT schema_name FROM public.tenants WHERE state = 1;")
        
        if not tenants:
            print("No active tenants found. Skipping tenant migrations.")
            
        for tenant in tenants:
            schema_name = tenant['schema_name']
            await apply_migrations_in_folder(conn, "migrations/tenants", schema_name)
            
        print("\n[SUCCESS] All database migrations applied successfully.")
    
    except Exception as e:
        print(f"\n[ERROR] Migration failed: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
