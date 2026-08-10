"""
cloud_models.py
ORM models for the PUBLIC schema tables: tenants + users.
These are the global, cross-tenant tables that exist outside any tenant schema.
"""
from sqlalchemy import (
    Column,
    Integer,
    String,
    SmallInteger,
    TIMESTAMP,
    ForeignKey,
    func,
)
from app.db.database import Base


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
    # e.g. 'TENANT_OWNER', 'SUPER_ADMIN'
    role = Column(String(50), nullable=False, default="TENANT_OWNER")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
