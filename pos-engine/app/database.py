import os 
from contextlib import asynccontextmanager
import asyncpg

DATABASE_URL = os.getenv()

async def init_db():
    """ intiializes the data base by building the tables"""
    schema_path = os.path.join(os.path.dirname(__file__), "..", "init_schema.sql")

    with open(schema_path, "r") as f:
        schema_sql = f.read()

    #connect to data base (postgre)
    conn = await asyncpg.connect(DATABASE_URL)

    try:
        #execute inside transaction to ensure the entire file executes
        async with conn.transaction():
            await conn.execute(schema_sql)
            print("The data base was successfully initialized")
    finally:
        #close the connection
        await conn.close()

