CREATE TYPE tenant_status AS ENUM ('pending_payment', 'active', 'past_due', 'canceled');

CREATE TABLE tenants (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    schema_name VARCHAR(100) UNIQUE NOT NULL,
    state INT DEFAULT 0 NOT NULL, -- 0 = pending, 1 = active
    payment_session_id VARCHAR(255) UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TYPE cloud_role AS ENUM (
    'SUPER_ADMIN',
    'TENANT_OWNER',
    'TENANT_ADMIN',
    'ACCOUNTANT',
    'OPERATIONS_MANAGER',
    'MARKETING_MANAGER',
    'ANALYST',
    'VIEWER'
);

CREATE TABLE users (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tenant_id INT NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role cloud_role NOT NULL DEFAULT 'VIEWER',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,

    CONSTRAINT fk_user_tenant FOREIGN KEY (tenant_id) REFERENCES tenants (id) ON DELETE CASCADE
);