-- ============================================================================
-- FILE: tenant_schema.sql
-- DESCRIPTION: The isolated blueprint for a single business's POS data.
-- NOTE: All tenant_id columns have been strictly removed for schema-level isolation.
-- ============================================================================

-- 1. BASE ENTITIES (No dependencies)
CREATE TABLE roles (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE permissions (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    code VARCHAR(100) NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE branches (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE employees (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    date_of_birth DATE,
    phone VARCHAR(50),
    pin_hash VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE warehouse_items (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    sku VARCHAR(100) UNIQUE,
    unit_of_measure VARCHAR(50) NOT NULL,
    minimum_stock NUMERIC(12, 3) DEFAULT 0 NOT NULL
);


-- 2. MAPPING & RELATIONSHIP TABLES
CREATE TABLE role_permissions (
    role_id INT REFERENCES roles(id) ON DELETE CASCADE,
    permission_id INT REFERENCES permissions(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);

CREATE TABLE branch_employees (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    employee_id INT REFERENCES employees(id) ON DELETE CASCADE NOT NULL,
    branch_id INT REFERENCES branches(id) ON DELETE CASCADE NOT NULL,
    role_id INT REFERENCES roles(id) ON DELETE SET NULL,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    removed_at TIMESTAMP WITH TIME ZONE
);


-- 3. INVENTORY & PRODUCTS
CREATE TABLE inventory_warehouse (
    warehouse_item_id INT PRIMARY KEY REFERENCES warehouse_items(id) ON DELETE CASCADE,
    quantity NUMERIC(12, 3) DEFAULT 0 NOT NULL
);

CREATE TABLE products (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price NUMERIC(12, 2) NOT NULL,
    is_recipe BOOLEAN DEFAULT FALSE NOT NULL,
    direct_warehouse_item_id INT REFERENCES warehouse_items(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE product_recipes (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id INT REFERENCES products(id) ON DELETE CASCADE NOT NULL,
    warehouse_item_id INT REFERENCES warehouse_items(id) ON DELETE CASCADE NOT NULL,
    quantity_required NUMERIC(12, 3) NOT NULL,
    UNIQUE (product_id, warehouse_item_id)
);


-- 4. OPERATIONS (Shifts & Orders)
CREATE TABLE shifts (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    employee_id INT REFERENCES employees(id) ON DELETE RESTRICT NOT NULL,
    branch_id INT REFERENCES branches(id) ON DELETE RESTRICT NOT NULL,
    opened_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    closed_at TIMESTAMP WITH TIME ZONE,
    opening_cash NUMERIC(12, 2) NOT NULL,
    closing_cash NUMERIC(12, 2)
);

CREATE TABLE cash_transactions (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    shift_id INT REFERENCES shifts(id) ON DELETE CASCADE NOT NULL,
    employee_id INT REFERENCES employees(id) ON DELETE RESTRICT NOT NULL,
    amount NUMERIC(12, 2) NOT NULL,
    transaction_type VARCHAR(50) NOT NULL CHECK (transaction_type IN ('PAY_IN', 'PAY_OUT')),
    reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE orders (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    branch_id INT REFERENCES branches(id) ON DELETE RESTRICT NOT NULL,
    employee_id INT REFERENCES employees(id) ON DELETE RESTRICT NOT NULL,
    order_number VARCHAR(100) UNIQUE NOT NULL,
    status VARCHAR(50) NOT NULL,
    total_amount NUMERIC(12, 2) DEFAULT 0 NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE order_line_items (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id INT REFERENCES orders(id) ON DELETE CASCADE NOT NULL,
    product_id INT REFERENCES products(id) ON DELETE RESTRICT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(12, 2) NOT NULL,
    subtotal_price NUMERIC(12, 2) NOT NULL
);

CREATE TABLE payments (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id INT REFERENCES orders(id) ON DELETE CASCADE NOT NULL,
    amount NUMERIC(12, 2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    reference_number VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE inventory_transactions (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    warehouse_item_id INT REFERENCES warehouse_items(id) ON DELETE RESTRICT NOT NULL,
    employee_id INT REFERENCES employees(id) ON DELETE RESTRICT NOT NULL,
    quantity_change NUMERIC(12, 3) NOT NULL,
    transaction_type VARCHAR(50) NOT NULL,
    reference_type VARCHAR(50),
    reference_id INT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);


-- 5. AUDITING
CREATE TABLE audit_logs (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    employee_id INT REFERENCES employees(id) ON DELETE SET NULL,
    table_name VARCHAR(100) NOT NULL,
    record_id INT NOT NULL,
    action VARCHAR(50) NOT NULL,
    old_value JSONB,
    new_value JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);