# API Specification

This document defines the API endpoints exposed by the backend and the communication contract between client applications and backend services.

---

# Authentication

## Cloud Login

Purpose:
Authenticates Super Admins and Tenant Admins to access the Cloud Dashboard.

Endpoint:
POST /cloud/auth/login

Authentication:
Public

Request Body:
username, password

Response:
JWT Access Token

---

## Tenant Registration & Payment (Self-Serve)

Purpose:
Registers a new tenant and initiates a Stripe Checkout session. The tenant is saved in a pending state until payment completes.

Endpoint:
POST /cloud/auth/register

Authentication:
Public

Request Body:
name, email, password

Response:
tenant_id, checkout_url, session_id

---

## Stripe Webhook Activation

Purpose:
Receives Stripe webhook notifications (specifically `checkout.session.completed`). Validates the webhook signature, provisions the isolated PostgreSQL schema for the tenant, applies `tenant_schema.sql`, creates the initial TENANT_OWNER user, and activates tenant state.

Endpoint:
POST /cloud/auth/stripe-webhook

Authentication:
Public (Stripe Signature Header Verified)

---

## Stripe Payment Verification (Dev/Test)

Purpose:
Manually verifies payment completion for a Stripe session ID in test/development environments to immediately trigger schema creation and tenant activation.

Endpoint:
POST /cloud/auth/verify-payment/{session_id}

Authentication:
Public

---

## POS Login

Purpose:
Authenticates an employee to a specific branch on a POS device using their auto-generated numeric ID and optional PIN.

Endpoint:
POST /pos/auth/login

Authentication:
Public

Request Body:
employee_id, pin (optional), branch_id

Response:
Session token containing branch-scoped permission data

---

## POS Logout

Purpose:
Invalidates the active session for the authenticated employee on the current device.

Endpoint:
POST /pos/auth/logout

Authentication:
Employee session token

---

# Super Admin

Super Admin accounts are seeded into the database and exist outside the tenant hierarchy.

## Tenant Management

POST /cloud/tenants

Purpose:
Creates a new tenant and generates a one-time registration code for the tenant owner. The tenant remains in a pending state until the first Tenant Admin completes registration.

Request Body:
name

Response:
tenant_id, registration_code, registration_expires_at
---

GET /cloud/tenants

Purpose:
Returns all tenants registered within the platform.

---

GET /cloud/tenants/{tenant_id}

Purpose:
Returns metadata and status for a single tenant.

---

PUT /cloud/tenants/{tenant_id}

Purpose:
Updates tenant metadata or operational status.

Request Body:
name, active

---

DELETE /cloud/tenants/{tenant_id}

Purpose:
Permanently removes a tenant. Intended only for accidental provisioning during administrative operations.

---

# Tenant Admin

All endpoints in this section are scoped to the authenticated tenant. tenant_id is resolved from the JWT and never accepted as a request parameter.

## Branch Management

POST /cloud/branches

Purpose:
Creates a new branch belonging to the authenticated tenant.

Request Body:
name, address

---

GET /cloud/branches

Purpose:
Returns all branches belonging to the authenticated tenant.

---

GET /cloud/branches/{branch_id}

Purpose:
Returns details for a single branch.

---

PUT /cloud/branches/{branch_id}

Purpose:
Updates branch information or operational status.

Request Body:
name, address, active

---

## Employee Management

POST /cloud/employees

Purpose:
Creates a new employee record under the authenticated tenant.

Request Body:
name, date_of_birth, phone

---

GET /cloud/employees

Purpose:
Returns all employees belonging to the authenticated tenant.

---

GET /cloud/employees/{employee_id}

Purpose:
Returns detailed information for a single employee.

---

PUT /cloud/employees/{employee_id}

Purpose:
Updates employee personal information.

Request Body:
name, date_of_birth, phone

---

DELETE /cloud/employees/{employee_id}

Purpose:
Removes an employee from active operation.

---

## Branch Assignment Management

POST /cloud/employees/{employee_id}/assignments

Purpose:
Assigns an employee to a branch with a specific role. An employee may be assigned to multiple branches but can only hold one role per branch.

Request Body:
branch_id, role_id

---

PUT /cloud/employees/{employee_id}/assignments/{branch_id}

Purpose:
Updates the role assigned to an employee at a specific branch.

Request Body:
role_id

---

DELETE /cloud/employees/{employee_id}/assignments/{branch_id}

Purpose:
Removes an employee from a branch. Access to that branch is immediately revoked.

---

## Role Management

POST /cloud/roles

Purpose:
Creates a new role for the authenticated tenant.

Request Body:
name, permission_codes (array)

---

GET /cloud/roles

Purpose:
Returns all roles available within the authenticated tenant.

---

GET /cloud/roles/{role_id}

Purpose:
Returns detailed information for a specific role including assigned permissions.

---

PUT /cloud/roles/{role_id}

Purpose:
Updates role name or its assigned permission set.

Request Body:
name, permission_codes (array)

---

DELETE /cloud/roles/{role_id}

Purpose:
Removes a role. Blocked if the role is currently assigned to any active branch assignment.

---

## Permission Reference

GET /cloud/permissions

Purpose:
Returns the full list of system-defined permissions available for assignment to roles. Permissions are predefined and cannot be created, modified, or deleted.

---

## Warehouse Item Management

POST /cloud/items

Purpose:
Creates a new warehouse inventory item.

Request Body:
name, sku, unit_of_measure, minimum_stock

---

GET /cloud/items

Purpose:
Returns all warehouse items belonging to the authenticated tenant.

---

GET /cloud/items/{item_id}

Purpose:
Returns details for a single warehouse item including current stock level.

---

PUT /cloud/items/{item_id}

Purpose:
Updates warehouse item information.

Request Body:
name, sku, unit_of_measure, minimum_stock

---

DELETE /cloud/items/{item_id}

Purpose:
Removes a warehouse item. Blocked if the item is referenced by any product or product recipe.

---

## Product Management

POST /cloud/products

Purpose:
Creates a new product. If is_recipe is false, a direct_warehouse_item_id must be provided. If is_recipe is true, recipe components must be submitted alongside.

Request Body:
name, price, is_recipe, direct_warehouse_item_id, recipe (array of warehouse_item_id and quantity_required)

---

GET /cloud/products

Purpose:
Returns all products belonging to the authenticated tenant.

---

GET /cloud/products/{product_id}

Purpose:
Returns product details. If the product is a recipe, the full ingredient list is included.

---

PUT /cloud/products/{product_id}

Purpose:
Updates product information, pricing, or recipe composition.

Request Body:
name, price, active, direct_warehouse_item_id, recipe (array of warehouse_item_id and quantity_required)

---

DELETE /cloud/products/{product_id}

Purpose:
Removes a product. Blocked if the product is referenced by existing order line items.

---

## Report management

GET /cloud/reports/sales

Purpose:
Returns sales summary data for the authenticated tenant. Supports filtering by branch_id, date range, and employee_id.

---

GET /cloud/reports/inventory

Purpose:
Returns current stock levels for all warehouse items. Flags items below their minimum_stock threshold.

---

GET /cloud/reports/shifts

Purpose:
Returns shift records with opening and closing cash reconciliation data. Supports filtering by branch_id and date range.

---

# POS Application

All endpoints in this section require a valid employee session token. Permissions are evaluated per request against the role assigned to the employee for the branch embedded in the session.

## Shift Management

POST /pos/shifts

Purpose:
Opens a new shift for the authenticated employee at their assigned branch. Records opening cash amount.

Request Body:
opening_cash

---

PUT /pos/shifts/{shift_id}

Purpose:
Closes an active shift. Records closing cash amount and timestamps the closure.

Request Body:
closing_cash

---

GET /pos/shifts/{shift_id}/summary

Purpose:
Returns shift metrics for the current shift including sales totals, cash movements, and order count. Requires sales.read_shift permission.

---

## Order Management

POST /pos/orders

Purpose:
Creates a new order or submits a held order for payment processing. Triggers atomic inventory deduction for all line items. For recipe products, all ingredient quantities are deducted in a single transaction. If any ingredient is insufficient, the transaction is rolled back.

Request Body:
line_items (array of product_id and quantity), discount_amount

---

GET /pos/orders

Purpose:
Returns orders for the current shift. Requires order.preview permission.

---

GET /pos/orders/{order_id}

Purpose:
Returns full details for a single order including line items and payment. Requires order.preview permission.

---

PUT /pos/orders/{order_id}

Purpose:
Updates order status. Used to void an active order or process a refund on a completed order. Void requires order.void permission. Refund requires order.refund permission.

Request Body:
action (void or refund), reason

---

## Cash Operations

POST /pos/cash/pay-in

Purpose:
Records a manual cash addition to the drawer for the current shift. Requires cash.pay_in permission.

Request Body:
amount, note

---

POST /pos/cash/pay-out

Purpose:
Records a manual cash withdrawal from the drawer for the current shift. Requires cash.pay_out permission.

Request Body:
amount, note

---

POST /pos/cash/open-drawer

Purpose:
Triggers the physical cash drawer without an associated sale. Requires cash.open_drawer permission.

---

## Check-In

POST /pos/check-in

Purpose:
Records a timestamped check-in or check-out event for the authenticated employee. Status is toggled based on their last recorded entry.