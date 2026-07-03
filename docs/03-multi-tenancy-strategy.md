This project uses Schema-Level Isolation.

Each tenant is assigned its own database schema containing its own tables (employees, branches, products, inventory, orders, etc.). When a user authenticates, the backend identifies the tenant from the JWT access token and executes all database operations within that tenant's schema.

Schema-Level Isolation was selected because the system is designed for independent businesses that require strict separation of their data. This approach minimizes the risk of cross-tenant data access, simplifies backup and recovery for individual tenants, and provides better security than Row-Level Isolation while remaining suitable for the expected scale of the application.