-- ============================================================================
-- PROJECT: Enterprise Multi-Tenant POS Engine
-- FILE: init_schema.sql
-- DESCRIPTION: Core database initialization script.
-- ============================================================================

-- ============================================================================
-- MODULE 1: CORE TENANCY & ORGANIZATION
-- ============================================================================

CREATE TABLE tenants (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE branches (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tenant_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    address TEXT NOT NULL,
    active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    CONSTRAINT fk_branch_tenant FOREIGN KEY (tenant_id) REFERENCES tenants (id) ON DELETE CASCADE
);
CREATE INDEX idx_branches_tenant_id ON branches(tenant_id);

-- ============================================================================
-- MODULE 2: USERS, SHIFTS & ROLE-BASED ACCESS CONTROL (RBAC)
-- ============================================================================

CREATE TABLE employees (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tenant_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    date_of_birth DATE,
    phone VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,

    CONSTRAINT fk_employee_tenant FOREIGN KEY (tenant_id) REFERENCES tenants (id) ON DELETE CASCADE
);
CREATE INDEX idx_employees_tenant_id ON employees(tenant_id);

CREATE TABLE roles (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tenant_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,

    CONSTRAINT fk_role_tenant FOREIGN KEY (tenant_id) REFERENCES tenants (id) ON DELETE CASCADE
);
CREATE INDEX idx_roles_tenant_id ON roles(tenant_id);

CREATE TABLE perms (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    code VARCHAR(100) UNIQUE NOT NULL,
    description TEXT
);

CREATE TABLE role_perms (
    role_id INT NOT NULL,
    perms_id INT NOT NULL,
    PRIMARY KEY (role_id, perms_id),

    CONSTRAINT fk_rp_role FOREIGN KEY (role_id) REFERENCES roles (id) ON DELETE CASCADE,
    CONSTRAINT fk_rp_perms FOREIGN KEY (perms_id) REFERENCES perms (id) ON DELETE CASCADE
);

CREATE TABLE branch_employee (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tenant_id INT NOT NULL,
    employee_id INT NOT NULL,
    branch_id INT NOT NULL,
    role_id INT NOT NULL,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    removed_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT fk_be_tenant FOREIGN KEY (tenant_id) REFERENCES tenants (id) ON DELETE CASCADE,
    CONSTRAINT fk_be_employee FOREIGN KEY (employee_id) REFERENCES employees (id) ON DELETE CASCADE,
    CONSTRAINT fk_be_branch FOREIGN KEY (branch_id) REFERENCES branches (id) ON DELETE CASCADE,
    CONSTRAINT fk_be_role FOREIGN KEY (role_id) REFERENCES roles (id) ON DELETE CASCADE
);
CREATE INDEX idx_be_tenant_id ON branch_employee(tenant_id);
CREATE INDEX idx_be_employee_id ON branch_employee(employee_id);

CREATE TABLE shifts (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tenant_id INT NOT NULL,
    employee_id INT NOT NULL,
    branch_id INT NOT NULL,
    opened_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    closed_at TIMESTAMP WITH TIME ZONE,
    opening_cash NUMERIC(12, 2) NOT NULL,
    closing_cash NUMERIC(12, 2),

    CONSTRAINT fk_shift_tenant FOREIGN KEY (tenant_id) REFERENCES tenants (id) ON DELETE CASCADE,
    CONSTRAINT fk_shift_employee FOREIGN KEY (employee_id) REFERENCES employees (id) ON DELETE CASCADE,
    CONSTRAINT fk_shift_branch FOREIGN KEY (branch_id) REFERENCES branches (id) ON DELETE CASCADE
);
CREATE INDEX idx_shifts_tenant_id ON shifts(tenant_id);

-- ============================================================================
-- MODULE 3: CATALOG & INVENTORY MANAGEMENT
-- ============================================================================

CREATE TABLE warehouse_items (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tenant_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    sku VARCHAR(100),
    unit_of_measure VARCHAR(50) NOT NULL,
    minimum_stock NUMERIC(12, 4) DEFAULT 0 NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,

    CONSTRAINT fk_wi_tenant FOREIGN KEY (tenant_id) REFERENCES tenants (id) ON DELETE CASCADE
);
CREATE INDEX idx_wi_tenant_id ON warehouse_items(tenant_id);

CREATE TABLE inventory_warehouse (
    tenant_id INT NOT NULL,
    warehouse_item_id INT NOT NULL,
    quantity NUMERIC(12, 4) DEFAULT 0 NOT NULL,
    
    PRIMARY KEY (tenant_id, warehouse_item_id),
    CONSTRAINT fk_iw_tenant FOREIGN KEY (tenant_id) REFERENCES tenants (id) ON DELETE CASCADE,
    CONSTRAINT fk_iw_item FOREIGN KEY (warehouse_item_id) REFERENCES warehouse_items (id) ON DELETE CASCADE
);

CREATE TABLE products (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tenant_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    price NUMERIC(12, 2) NOT NULL,
    is_recipe BOOLEAN DEFAULT FALSE NOT NULL,
    direct_warehouse_item_id INT,
    active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,

    CONSTRAINT fk_product_tenant FOREIGN KEY (tenant_id) REFERENCES tenants (id) ON DELETE CASCADE,
    CONSTRAINT fk_product_direct_item FOREIGN KEY (direct_warehouse_item_id) REFERENCES warehouse_items (id) ON DELETE SET NULL
);
CREATE INDEX idx_products_tenant_id ON products(tenant_id);

CREATE TABLE product_recipes (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id INT NOT NULL,
    warehouse_item_id INT NOT NULL,
    quantity_required NUMERIC(12, 4) NOT NULL,

    CONSTRAINT unq_product_item UNIQUE (product_id, warehouse_item_id),
    CONSTRAINT fk_pr_product FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE,
    CONSTRAINT fk_pr_item FOREIGN KEY (warehouse_item_id) REFERENCES warehouse_items (id) ON DELETE CASCADE
);

-- ============================================================================
-- MODULE 4: SALES, ORDERS, FINANCE & AUDIT
-- ============================================================================

CREATE TABLE orders (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tenant_id INT NOT NULL,
    branch_id INT NOT NULL,
    employee_id INT NOT NULL,
    order_number VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    total_amount NUMERIC(12, 2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,

    CONSTRAINT fk_order_tenant FOREIGN KEY (tenant_id) REFERENCES tenants (id) ON DELETE CASCADE,
    CONSTRAINT fk_order_branch FOREIGN KEY (branch_id) REFERENCES branches (id) ON DELETE CASCADE,
    CONSTRAINT fk_order_employee FOREIGN KEY (employee_id) REFERENCES employees (id) ON DELETE CASCADE
);
CREATE INDEX idx_orders_tenant_id ON orders(tenant_id);
CREATE INDEX idx_orders_number ON orders(order_number);

CREATE TABLE order_line_items (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tenant_id INT NOT NULL,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price NUMERIC(12, 2) NOT NULL,
    subtotal_price NUMERIC(12, 2) NOT NULL,

    CONSTRAINT fk_oli_tenant FOREIGN KEY (tenant_id) REFERENCES tenants (id) ON DELETE CASCADE,
    CONSTRAINT fk_oli_order FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE CASCADE,
    CONSTRAINT fk_oli_product FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE RESTRICT
);
CREATE INDEX idx_oli_tenant_id ON order_line_items(tenant_id);

CREATE TABLE payments (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tenant_id INT NOT NULL,
    order_id INT NOT NULL,
    amount NUMERIC(12, 2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    reference_number VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,

    CONSTRAINT fk_payment_tenant FOREIGN KEY (tenant_id) REFERENCES tenants (id) ON DELETE CASCADE,
    CONSTRAINT fk_payment_order FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE CASCADE
);
CREATE INDEX idx_payments_tenant_id ON payments(tenant_id);

CREATE TABLE inventory_transactions (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tenant_id INT NOT NULL,
    warehouse_item_id INT NOT NULL,
    employee_id INT NOT NULL,
    quantity_change NUMERIC(12, 4) NOT NULL,
    transaction_type VARCHAR(50) NOT NULL,
    reference_type VARCHAR(50) NOT NULL,
    reference_id INT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,

    CONSTRAINT fk_it_tenant FOREIGN KEY (tenant_id) REFERENCES tenants (id) ON DELETE CASCADE,
    CONSTRAINT fk_it_item FOREIGN KEY (warehouse_item_id) REFERENCES warehouse_items (id) ON DELETE CASCADE,
    CONSTRAINT fk_it_employee FOREIGN KEY (employee_id) REFERENCES employees (id) ON DELETE RESTRICT
);
CREATE INDEX idx_it_tenant_id ON inventory_transactions(tenant_id);
CREATE INDEX idx_it_item_id ON inventory_transactions(warehouse_item_id);

CREATE TABLE audit_logs (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tenant_id INT NOT NULL,
    employee_id INT,
    table_name VARCHAR(100) NOT NULL,
    record_id INT NOT NULL,
    action VARCHAR(50) NOT NULL,
    old_value JSONB,
    new_value JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,

    CONSTRAINT fk_audit_tenant FOREIGN KEY (tenant_id) REFERENCES tenants (id) ON DELETE CASCADE
);
CREATE INDEX idx_audit_logs_tenant_id ON audit_logs(tenant_id);
CREATE INDEX idx_audit_logs_table_record ON audit_logs(table_name, record_id);