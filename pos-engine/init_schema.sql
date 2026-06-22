CREATE TABLE tenants (
    id INT GENERATED ALWAYS AS IDENTITY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE products (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tenant_id INT NOT NULL REFERENCES tenants(id),
    name VARCHAR(100) NOT NULL
);

CREATE TABLE inventory_warehouse (
    tenant_id INT NOT NULL REFERENCES tenant(id),
    product_id INT NOT NULL REFERENCES tenant(id),
    quantity INT NOT NULL CHECK (quantity >= 0 ),
    PRIMARY KEY (tenant_id, product_id)
);

