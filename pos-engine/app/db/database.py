import asyncpg
import os
from typing import AsyncGenerator

db_pool: asyncpg.Pool | None = None

async def create_db_pool():
    global db_pool
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:123123@localhost:5432/POS-ENGINE")

    try:
        db_pool = await asyncpg.create_pool(
            dsn = DATABASE_URL,
            min_size=2,
            max_size=10
        )

        print("Data base connection pool initialized.")
    except Exception as e:
        print("failed to intialize pool")
        raise e

async def close_db_pool():
    global db_pool
    if db_pool:
        await db_pool.close()
        print("data base connection pool closed.")

async def get_db_connection() -> AsyncGenerator[asyncpg.Connection, None]:
    if db.pool is None:
        raise Exception("Data base pool is not initialized")

    async with db_pool.acquire() as connection:
        yield connection