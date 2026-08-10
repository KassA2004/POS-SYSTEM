import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text

# asyncpg driver requires the postgresql+asyncpg:// scheme
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:123123@localhost:5432/POS-ENGINE")

# pool_size=2 kept connections always-ready; max_overflow=10 allows burst headroom
engine = create_async_engine(
    DATABASE_URL,
    pool_size=2,
    max_overflow=10,
    pool_pre_ping=True,   # drops stale connections before handing them out
    echo=False,
)

# expire_on_commit=False keeps ORM objects usable after commit without re-querying
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()


# ---------------------------------------------------------------------------
# Dependency: plain session (public schema — used by auth / tenants routes)
# ---------------------------------------------------------------------------
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Yields an AsyncSession bound to the public schema.
    Used by routes that don't need tenant-level routing (login, register, tenants list).
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ---------------------------------------------------------------------------
# Dependency: tenant-scoped session
# ---------------------------------------------------------------------------
async def get_tenant_db(schema_name: str) -> AsyncGenerator[AsyncSession, None]:
    """
    Yields an AsyncSession with search_path set to the given tenant schema.
    Replicates the old `SET search_path TO {schema_name}` asyncpg pattern.

    Usage inside a FastAPI dependency:
        async def get_scoped_db(
            current_user: dict = Depends(get_current_tenant_user),
        ) -> AsyncGenerator[AsyncSession, None]:
            async for session in get_tenant_db(current_user["schema_name"]):
                yield session
    """
    async with AsyncSessionLocal() as session:
        # Route this session to the tenant's isolated schema
        await session.execute(text(f"SET search_path TO {schema_name}"))
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ---------------------------------------------------------------------------
# Lifecycle hooks (called from main.py lifespan)
# ---------------------------------------------------------------------------
async def create_db_pool():
    """Startup hook. The SQLAlchemy engine pool initialises lazily on first use."""
    print("Database connection pool initialised via SQLAlchemy.")


async def close_db_pool():
    """Shutdown hook. Disposes the engine connection pool gracefully."""
    await engine.dispose()
    print("Database connection pool closed.")