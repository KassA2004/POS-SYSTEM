-- Public schema initial migration
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tenant_status') THEN
        CREATE TYPE tenant_status AS ENUM ('pending_payment', 'active', 'past_due', 'canceled');
    END IF;
END $$;

CREATE TABLE IF NOT EXISTS tenants (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    schema_name VARCHAR(100) UNIQUE NOT NULL,
    state INT DEFAULT 0 NOT NULL, -- 0 = pending, 1 = active
    payment_session_id VARCHAR(255) UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

ALTER TABLE tenants ADD COLUMN IF NOT EXISTS state INT DEFAULT 0 NOT NULL;
ALTER TABLE tenants ADD COLUMN IF NOT EXISTS payment_session_id VARCHAR(255) UNIQUE;

DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'cloud_role') THEN
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
    END IF;
END $$;

CREATE TABLE IF NOT EXISTS users (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tenant_id INT NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role cloud_role NOT NULL DEFAULT 'VIEWER',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,

    CONSTRAINT fk_user_tenant FOREIGN KEY (tenant_id) REFERENCES tenants (id) ON DELETE CASCADE
);
