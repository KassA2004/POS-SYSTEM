"""
cloud_models.py
ORM models for the PUBLIC schema tables: tenants + users.
These are the global, cross-tenant tables that exist outside any tenant schema.
"""
import enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    SmallInteger,
    TIMESTAMP,
    ForeignKey,
    Enum,
    func,
)
from app.db.database import Base


class CloudRole(str, enum.Enum):
    """Mirrors the `cloud_role` PostgreSQL enum defined in init_schema.sql."""
    SUPER_ADMIN = "SUPER_ADMIN"
    TENANT_OWNER = "TENANT_OWNER"
    TENANT_ADMIN = "TENANT_ADMIN"
    ACCOUNTANT = "ACCOUNTANT"
    OPERATIONS_MANAGER = "OPERATIONS_MANAGER"
    MARKETING_MANAGER = "MARKETING_MANAGER"
    ANALYST = "ANALYST"
    VIEWER = "VIEWER"


class Tenant(Base):
    """Mirrors the `tenants` table in the public schema."""
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    schema_name = Column(String(255), nullable=False, unique=True)
    # 0 = pending payment, 1 = active
    state = Column(SmallInteger, nullable=False, default=0)
    payment_session_id = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)


class User(Base):
    """Mirrors the `users` table in the public schema."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    # Uses the existing `cloud_role` PostgreSQL enum — create_type=False prevents
    # SQLAlchemy from trying to CREATE TYPE (it already exists in the DB).
    role = Column(
        Enum(
            CloudRole,
            name="cloud_role",
            create_type=False,
        ),
        nullable=False,
        default=CloudRole.TENANT_OWNER,
    )
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
