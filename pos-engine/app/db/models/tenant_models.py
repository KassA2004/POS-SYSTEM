"""
tenant_models.py
ORM models for every table defined in tenant_schema.sql.

IMPORTANT — Schema routing strategy:
    These models do NOT hard-code a schema= argument on their Table.
    Schema isolation is achieved at connection time via:
        SET search_path TO {schema_name}
    …which is exactly how the legacy asyncpg code worked, and is handled
    by the `get_tenant_db` dependency in database.py.
"""
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    ForeignKey,
    Integer,
    JSON,
    Numeric,
    String,
    TIMESTAMP,
    Text,
    UniqueConstraint,
    func,
)
from app.db.database import Base


# =============================================================================
# 1. BASE ENTITIES (no foreign-key dependencies)
# =============================================================================

class Role(Base):
    """Mirrors the `roles` table."""
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)


class Permission(Base):
    """Mirrors the `permissions` table."""
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)


class Branch(Base):
    """Mirrors the `branches` table."""
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    address = Column(Text, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)


class Employee(Base):
    """Mirrors the `employees` table."""
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    date_of_birth = Column(Date, nullable=True)
    phone = Column(String(50), nullable=True)
    pin_hash = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)


class WarehouseItem(Base):
    """Mirrors the `warehouse_items` table."""
    __tablename__ = "warehouse_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    sku = Column(String(100), nullable=True, unique=True)
    unit_of_measure = Column(String(50), nullable=False)
    minimum_stock = Column(Numeric(12, 3), nullable=False, default=0)


# =============================================================================
# 2. MAPPING & RELATIONSHIP TABLES
# =============================================================================

class RolePermission(Base):
    """Mirrors the `role_permissions` join table."""
    __tablename__ = "role_permissions"

    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    permission_id = Column(Integer, ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True)


class BranchEmployee(Base):
    """Mirrors the `branch_employees` table (soft-delete via removed_at)."""
    __tablename__ = "branch_employees"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id", ondelete="CASCADE"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="SET NULL"), nullable=True)
    assigned_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    removed_at = Column(TIMESTAMP(timezone=True), nullable=True)


# =============================================================================
# 3. INVENTORY & PRODUCTS
# =============================================================================

class InventoryWarehouse(Base):
    """Mirrors the `inventory_warehouse` table."""
    __tablename__ = "inventory_warehouse"

    # Primary key is also a FK — same pattern as the SQL
    warehouse_item_id = Column(
        Integer,
        ForeignKey("warehouse_items.id", ondelete="CASCADE"),
        primary_key=True,
    )
    quantity = Column(Numeric(12, 3), nullable=False, default=0)


class Product(Base):
    """Mirrors the `products` table."""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    price = Column(Numeric(12, 2), nullable=False)
    is_recipe = Column(Boolean, nullable=False, default=False)
    direct_warehouse_item_id = Column(
        Integer,
        ForeignKey("warehouse_items.id", ondelete="SET NULL"),
        nullable=True,
    )
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)


class ProductRecipe(Base):
    """Mirrors the `product_recipes` table."""
    __tablename__ = "product_recipes"
    __table_args__ = (
        UniqueConstraint("product_id", "warehouse_item_id", name="uq_product_recipe_ingredient"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    warehouse_item_id = Column(Integer, ForeignKey("warehouse_items.id", ondelete="CASCADE"), nullable=False)
    quantity_required = Column(Numeric(12, 3), nullable=False)


# =============================================================================
# 4. OPERATIONS (Shifts, Orders, Payments)
# =============================================================================

class Shift(Base):
    """Mirrors the `shifts` table."""
    __tablename__ = "shifts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="RESTRICT"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id", ondelete="RESTRICT"), nullable=False)
    opened_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    closed_at = Column(TIMESTAMP(timezone=True), nullable=True)
    opening_cash = Column(Numeric(12, 2), nullable=False)
    closing_cash = Column(Numeric(12, 2), nullable=True)


class CashTransaction(Base):
    """Mirrors the `cash_transactions` table."""
    __tablename__ = "cash_transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    shift_id = Column(Integer, ForeignKey("shifts.id", ondelete="CASCADE"), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="RESTRICT"), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    transaction_type = Column(String(50), nullable=False)  # 'PAY_IN' | 'PAY_OUT'
    reason = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)


class Order(Base):
    """Mirrors the `orders` table."""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id", ondelete="RESTRICT"), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="RESTRICT"), nullable=False)
    order_number = Column(String(100), nullable=False, unique=True)
    status = Column(String(50), nullable=False)
    total_amount = Column(Numeric(12, 2), nullable=False, default=0)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class OrderLineItem(Base):
    """Mirrors the `order_line_items` table."""
    __tablename__ = "order_line_items"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_order_line_items_quantity_positive"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False)
    subtotal_price = Column(Numeric(12, 2), nullable=False)


class Payment(Base):
    """Mirrors the `payments` table."""
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    payment_method = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False)
    reference_number = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)


class InventoryTransaction(Base):
    """Mirrors the `inventory_transactions` table."""
    __tablename__ = "inventory_transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    warehouse_item_id = Column(Integer, ForeignKey("warehouse_items.id", ondelete="RESTRICT"), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="RESTRICT"), nullable=False)
    quantity_change = Column(Numeric(12, 3), nullable=False)
    transaction_type = Column(String(50), nullable=False)
    reference_type = Column(String(50), nullable=True)
    reference_id = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)


# =============================================================================
# 5. AUDITING
# =============================================================================

class AuditLog(Base):
    """Mirrors the `audit_logs` table."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="SET NULL"), nullable=True)
    table_name = Column(String(100), nullable=False)
    record_id = Column(Integer, nullable=False)
    action = Column(String(50), nullable=False)
    old_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
