import os
import asyncpg
from contextLib import asynccontextmanager

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:secret@localhost:5432/postgres")

db_pool: asyncpg.Pool = None

async def init_db_pool():

    global db_pool

    db_pool = await asyncpg.create_pool(
        dsn= DATABASE_URL,
        min_size=5,
        max_size=20
    )
    print("Database connection pool initialized.")

    async def close_db_pool():
        global db_pool
        if db_pool:
            await db_pool.close()
            print("Database connection pool closed.")

@asynccontextmanager

async def get_db_connection():
    global db_pool
    if db_pool is None:
        raise RuntimeException("Data base pool is not initialized")

    async with db_pool.acquire() as connection:
        yield connection