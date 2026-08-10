# Backend Implementation & Missing Endpoints Report

**File Path:** `docs/04-missing-endpoints-report.md`  
**Date:** August 2026  
**Scope:** POS System Engine (`pos-engine`) Backend API & Database Schema  
**Target Audience:** LLMs & Backend Developers  

---

## 1. Architectural & Specification Updates

### 1.1 Tenant Registration & Provisioning (Stripe Self-Serve Flow)
* **Old Specification (Deprecated):** Manual tenant creation by Super Admin generating a one-time registration code, validated via `POST /cloud/auth/validate-registration-code`.
* **Current Implementation (Active):** Self-serve registration driven by Stripe Integration:
  1. `POST /cloud/auth/register` accepts business `name`, `email`, and `password`. Creates a tenant in `pending` state (state 0) and generates a Stripe Checkout Session.
  2. Upon successful checkout, Stripe sends a webhook to `POST /cloud/auth/stripe-webhook` (`checkout.session.completed`).
  3. The service function `activate_tenant_and_create_schema` dynamically provisions a unique PostgreSQL schema (`tenant_<id>`), executes `tenant_schema.sql`, creates the initial `TENANT_OWNER` user record, and marks the tenant active (state 1).
  4. For development/testing, `POST /cloud/auth/verify-payment/{session_id}` provides instant activation.
* **Impact:** Super Admin tenant creation (`POST /cloud/tenants`) and registration code validation (`POST /cloud/auth/validate-registration-code`) are **no longer required**.

### 1.2 Database Schema Updates
* **Cash Operations Table:** The `cash_transactions` table has been added to [tenant_schema.sql](file:///c:/Users/t/Desktop/Projects/Programming/POS%20SYSTEM/pos-engine/tenant_schema.sql) (lines 97-105).
  ```sql
  CREATE TABLE cash_transactions (
      id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
      shift_id INT REFERENCES shifts(id) ON DELETE CASCADE NOT NULL,
      employee_id INT REFERENCES employees(id) ON DELETE RESTRICT NOT NULL,
      amount NUMERIC(12, 2) NOT NULL,
      transaction_type VARCHAR(50) NOT NULL CHECK (transaction_type IN ('PAY_IN', 'PAY_OUT')),
      reason TEXT,
      created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
  );
  ```
  *(Status: Completed)*

---

## 2. Implementation Status by Domain

Legend:
* ✅ **Implemented & Registered**: Code exists, tested/ready, and included in `app/main.py`.
* ⚠️ **Code Exists / Unregistered**: Code exists in `app/api/...` but router is not included in `app/main.py`.
* 🟡 **Partially Implemented**: Some CRUD routes exist (e.g. `POST`, `PUT`, `DELETE`), but `GET` (Read) routes are missing.
* 🔴 **Missing**: Endpoint or module is not yet implemented.

---

### 2.1 Authentication & Tenancy Management

| Endpoint | Method | Status | File Location / Implementation Notes |
| :--- | :--- | :--- | :--- |
| `/auth/login` | `POST` | ✅ Implemented | [app/api/cloud/auth/login.py](file:///c:/Users/t/Desktop/Projects/Programming/POS%20SYSTEM/pos-engine/app/api/cloud/auth/login.py) |
| `/auth/register` | `POST` | ✅ Implemented | [app/api/cloud/auth/registration.py](file:///c:/Users/t/Desktop/Projects/Programming/POS%20SYSTEM/pos-engine/app/api/cloud/auth/registration.py) |
| `/auth/stripe-webhook` | `POST` | ✅ Implemented | [app/api/cloud/auth/registration.py](file:///c:/Users/t/Desktop/Projects/Programming/POS%20SYSTEM/pos-engine/app/api/cloud/auth/registration.py) |
| `/auth/verify-payment/{session_id}` | `POST` | ✅ Implemented | [app/api/cloud/auth/registration.py](file:///c:/Users/t/Desktop/Projects/Programming/POS%20SYSTEM/pos-engine/app/api/cloud/auth/registration.py) |
| `/tenants` | `GET` | ✅ Implemented | [app/api/cloud/tenants.py](file:///c:/Users/t/Desktop/Projects/Programming/POS%20SYSTEM/pos-engine/app/api/cloud/tenants.py) |
| `/tenants/{tenant_id}` | `GET` | 🔴 Missing | Super Admin single tenant view |
| `/tenants/{tenant_id}` | `PUT` | 🔴 Missing | Super Admin tenant update (active state/name) |
| `/tenants/{tenant_id}` | `DELETE` | 🔴 Missing | Super Admin tenant delete |

---

### 2.2 Cloud Management Resources (Tenant-Scoped)

> **Core Pattern:** Most cloud entities currently implement `POST` (Create), `PUT` (Update), and `DELETE` (Delete), but **lack `GET` (List & Single Detail)** endpoints.

| Resource Domain | Method | Endpoint | Status | File Location / Gaps |
| :--- | :--- | :--- | :--- | :--- |
| **Branches** | `POST` | `/branches/` | ✅ Implemented | [app/api/cloud/branches.py](file:///c:/Users/t/Desktop/Projects/Programming/POS%20SYSTEM/pos-engine/app/api/cloud/branches.py) |
| | `DELETE` | `/branches/{branch_id}` | ✅ Implemented | [app/api/cloud/branches.py](file:///c:/Users/t/Desktop/Projects/Programming/POS%20SYSTEM/pos-engine/app/api/cloud/branches.py) |
| | `GET` | `/branches/` | 🔴 Missing | Need list all branches endpoint |
| | `GET` | `/branches/{branch_id}` | 🔴 Missing | Need single branch detail endpoint |
| | `PUT` | `/branches/{branch_id}` | 🔴 Missing | Need update branch endpoint |
| **Employees** | `POST` | `/employees/` | ✅ Implemented | [app/api/cloud/employees.py](file:///c:/Users/t/Desktop/Projects/Programming/POS%20SYSTEM/pos-engine/app/api/cloud/employees.py) |
| | `PUT` | `/employees/{employee_id}` | ✅ Implemented | [app/api/cloud/employees.py](file:///c:/Users/t/Desktop/Projects/Programming/POS%20SYSTEM/pos-engine/app/api/cloud/employees.py) |
| | `DELETE` | `/employees/{employee_id}` | ✅ Implemented | [app/api/cloud/employees.py](file:///c:/Users/t/Desktop/Projects/Programming/POS%20SYSTEM/pos-engine/app/api/cloud/employees.py) |
| | `GET` | `/employees/` | 🔴 Missing | Need list all employees endpoint |
| | `GET` | `/employees/{employee_id}` | 🔴 Missing | Need single employee detail endpoint |
| **Roles & Permissions** | `POST` | `/roles/` | ✅ Implemented | [app/api/cloud/roles.py](file:///c:/Users/t/Desktop/Projects/Programming/POS%20SYSTEM/pos-engine/app/api/cloud/roles.py) |
| | `PUT` | `/roles/{role_id}` | ✅ Implemented | [app/api/cloud/roles.py](file:///c:/Users/t/Desktop/Projects/Programming/POS%20SYSTEM/pos-engine/app/api/cloud/roles.py) |
| | `DELETE` | `/roles/{role_id}` | ✅ Implemented | [app/api/cloud/roles.py](file:///c:/Users/t/Desktop/Projects/Programming/POS%20SYSTEM/pos-engine/app/api/cloud/roles.py) |
| | `GET` | `/roles/` | 🔴 Missing | Need list all roles endpoint |
| | `GET` | `/roles/{role_id}` | 🔴 Missing | Need single role detail endpoint |
| | `GET` | `/permissions` | 🔴 Missing | Need permissions system list reference |
| **Branch Assignments** | `POST` | `/branches/{branch_id}/assign` | ✅ Implemented | [app/api/cloud/branch_employees.py](file:///c:/Users/t/Desktop/Projects/Programming/POS%20SYSTEM/pos-engine/app/api/cloud/branch_employees.py) |
| | `PUT` | `/branch-employees/{assignment_id}` | ✅ Implemented | [app/api/cloud/branch_employees.py](file:///c:/Users/t/Desktop/Projects/Programming/POS%20SYSTEM/pos-engine/app/api/cloud/branch_employees.py) |
| | `DELETE` | `/branch-employees/{assignment_id}` | ✅ Implemented | [app/api/cloud/branch_employees.py](file:///c:/Users/t/Desktop/Projects/Programming/POS%20SYSTEM/pos-engine/app/api/cloud/branch_employees.py) |
| | `GET` | `/employees/{employee_id}/assignments` | 🔴 Missing | List employee branch assignments |
| **Warehouse Items** | `POST` | `/warehouse-items/` | ✅ Implemented | [app/api/cloud/warehouse_items.py](file:///c:/Users/t/Desktop/Projects/Programming/POS%20SYSTEM/pos-engine/app/api/cloud/warehouse_items.py) |
| | `PUT` | `/warehouse-items/{item_id}` | ✅ Implemented | [app/api/cloud/warehouse_items.py](file:///c:/Users/t/Desktop/Projects/Programming/POS%20SYSTEM/pos-engine/app/api/cloud/warehouse_items.py) |
| | `DELETE` | `/warehouse-items/{item_id}` | ✅ Implemented | [app/api/cloud/warehouse_items.py](file:///c:/Users/t/Desktop/Projects/Programming/POS%20SYSTEM/pos-engine/app/api/cloud/warehouse_items.py) |
| | `GET` | `/warehouse-items/` | 🔴 Missing | Need list warehouse items endpoint |
| | `GET` | `/warehouse-items/{item_id}` | 🔴 Missing | Need single item detail endpoint |
| **Products & Recipes** | `POST` | `/products/` | ✅ Implemented | [app/api/cloud/products.py](file:///c:/Users/t/Desktop/Projects/Programming/POS%20SYSTEM/pos-engine/app/api/cloud/products.py) |
| | `PUT` | `/products/{product_id}` | ✅ Implemented | [app/api/cloud/products.py](file:///c:/Users/t/Desktop/Projects/Programming/POS%20SYSTEM/pos-engine/app/api/cloud/products.py) |
| | `DELETE` | `/products/{product_id}` | ✅ Implemented | [app/api/cloud/products.py](file:///c:/Users/t/Desktop/Projects/Programming/POS%20SYSTEM/pos-engine/app/api/cloud/products.py) |
| | `POST` | `/products/{product_id}/recipes` | ✅ Implemented | [app/api/cloud/products.py](file:///c:/Users/t/Desktop/Projects/Programming/POS%20SYSTEM/pos-engine/app/api/cloud/products.py) |
| | `PUT` | `/products/{product_id}/recipes/{recipe_id}` | ✅ Implemented | [app/api/cloud/products.py](file:///c:/Users/t/Desktop/Projects/Programming/POS%20SYSTEM/pos-engine/app/api/cloud/products.py) |
| | `DELETE` | `/products/{product_id}/recipes/{recipe_id}` | ✅ Implemented | [app/api/cloud/products.py](file:///c:/Users/t/Desktop/Projects/Programming/POS%20SYSTEM/pos-engine/app/api/cloud/products.py) |
| | `GET` | `/products/` | 🔴 Missing | Need list products endpoint |
| | `GET` | `/products/{product_id}` | 🔴 Missing | Need single product detail with recipe breakdown |

---

### 2.3 POS Application & Terminal Endpoints

| Resource / Functionality | Method | Endpoint | Status | File Location / Notes |
| :--- | :--- | :--- | :--- | :--- |
| **POS Auth** | `POST` | `/pos/auth/login` | 🔴 Missing | Employee ID + PIN login for POS terminal session |
| | `POST` | `/pos/auth/logout` | 🔴 Missing | Terminate POS session |
| **Shift Management** | `POST` | `/pos/shifts/` | ⚠️ Code Exists (Unregistered) | [app/api/pos/shifts.py](file:///c:/Users/t/Desktop/Projects/Programming/POS%20SYSTEM/pos-engine/app/api/pos/shifts.py) |
| | `PUT` | `/pos/shifts/{shift_id}` | ⚠️ Code Exists (Unregistered) | [app/api/pos/shifts.py](file:///c:/Users/t/Desktop/Projects/Programming/POS%20SYSTEM/pos-engine/app/api/pos/shifts.py) |
| | `GET` | `/pos/shifts/{shift_id}/summary` | ⚠️ Code Exists (Unregistered) | [app/api/pos/shifts.py](file:///c:/Users/t/Desktop/Projects/Programming/POS%20SYSTEM/pos-engine/app/api/pos/shifts.py) |
| **Warehouse Inventory** | `GET` | `/pos/inventory/` | ⚠️ Code Exists (Unregistered) | [app/api/pos/inventory_warehouse.py](file:///c:/Users/t/Desktop/Projects/Programming/POS%20SYSTEM/pos-engine/app/api/pos/inventory_warehouse.py) |
| | `GET` | `/pos/inventory/{item_id}` | ⚠️ Code Exists (Unregistered) | [app/api/pos/inventory_warehouse.py](file:///c:/Users/t/Desktop/Projects/Programming/POS%20SYSTEM/pos-engine/app/api/pos/inventory_warehouse.py) |
| | `PUT` | `/pos/inventory/{item_id}` | ⚠️ Code Exists (Unregistered) | [app/api/pos/inventory_warehouse.py](file:///c:/Users/t/Desktop/Projects/Programming/POS%20SYSTEM/pos-engine/app/api/pos/inventory_warehouse.py) |
| | `POST` | `/pos/inventory/` | ⚠️ Code Exists (Unregistered) | [app/api/pos/inventory_warehouse.py](file:///c:/Users/t/Desktop/Projects/Programming/POS%20SYSTEM/pos-engine/app/api/pos/inventory_warehouse.py) |
| **Order Management** | `POST` | `/pos/orders` | 🔴 Missing | Create order, record payments & atomic stock deduction (with recipe resolution) |
| | `GET` | `/pos/orders` | 🔴 Missing | List orders for current shift |
| | `GET` | `/pos/orders/{order_id}` | 🔴 Missing | Single order details |
| | `PUT` | `/pos/orders/{order_id}` | 🔴 Missing | Order void / refund actions |
| **Cash Operations** | `POST` | `/pos/cash/pay-in` | 🔴 Missing | Manual cash addition to drawer (populates `cash_transactions`) |
| | `POST` | `/pos/cash/pay-out` | 🔴 Missing | Manual cash withdrawal from drawer (populates `cash_transactions`) |
| | `POST` | `/pos/cash/open-drawer` | 🔴 Missing | Audit log trigger for opening cash drawer |
| **Employee Check-In** | `POST` | `/pos/check-in` | 🔴 Missing | Time tracking check-in/check-out toggle |

---

### 2.4 Reporting & Auditing

| Report / Feature | Method | Endpoint | Status | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Sales Report** | `GET` | `/cloud/reports/sales` | 🔴 Missing | Aggregated sales metrics (by branch, employee, date range) |
| **Inventory Report** | `GET` | `/cloud/reports/inventory` | 🔴 Missing | Warehouse stock levels flagged against `minimum_stock` |
| **Shift Report** | `GET` | `/cloud/reports/shifts` | 🔴 Missing | Shift cash reconciliation & variance reports |
| **Audit Logs** | N/A | N/A | 🔴 Missing | Database triggers / middleware to capture table changes into `audit_logs` |

---

## 3. Immediate Action Plan & Task Roadmap

For LLMs or developers continuing work on this codebase, tasks should be tackled in the following prioritized sequence:

### Phase 1: Router Registration & Basic Read Endpoints (Fast Completion)
1. **Register Routers in [app/main.py](file:///c:/Users/t/Desktop/Projects/Programming/POS%20SYSTEM/pos-engine/app/main.py):**
   - Import and include `pos.shifts.router` and `pos.inventory_warehouse.router`.
2. **Implement Missing `GET` Endpoints for Cloud Entities:**
   - [branches.py](file:///c:/Users/t/Desktop/Projects/Programming/POS%20SYSTEM/pos-engine/app/api/cloud/branches.py): Add `GET /branches/`, `GET /branches/{id}`, and `PUT /branches/{id}`.
   - [employees.py](file:///c:/Users/t/Desktop/Projects/Programming/POS%20SYSTEM/pos-engine/app/api/cloud/employees.py): Add `GET /employees/` and `GET /employees/{id}`.
   - [roles.py](file:///c:/Users/t/Desktop/Projects/Programming/POS%20SYSTEM/pos-engine/app/api/cloud/roles.py): Add `GET /roles/`, `GET /roles/{id}`, and `GET /permissions`.
   - [warehouse_items.py](file:///c:/Users/t/Desktop/Projects/Programming/POS%20SYSTEM/pos-engine/app/api/cloud/warehouse_items.py): Add `GET /warehouse-items/` and `GET /warehouse-items/{id}`.
   - [products.py](file:///c:/Users/t/Desktop/Projects/Programming/POS%20SYSTEM/pos-engine/app/api/cloud/products.py): Add `GET /products/` and `GET /products/{id}`.

### Phase 2: POS Authentication & Cash Operations
1. **Implement POS Authentication:**
   - Create `app/api/pos/auth.py` for `/pos/auth/login` (Employee numeric ID + PIN validation) and `/pos/auth/logout`.
2. **Implement Cash Operations:**
   - Create `app/api/pos/cash.py` for `/pos/cash/pay-in` and `/pos/cash/pay-out` to insert into `cash_transactions`.

### Phase 3: Order Execution & Inventory Deduction Engine
1. **Implement Order Service (`POST /pos/orders`):**
   - Atomically create order, line items, and payment.
   - Calculate recipe ingredients if `is_recipe = true` or direct warehouse item deduction.
   - Apply `FOR UPDATE` lock on `inventory_warehouse` rows.
   - Log movements in `inventory_transactions`.
2. **Implement Order Void / Refund (`PUT /pos/orders/{id}`):**
   - Handle status transitions (`voided`, `refunded`) and inverse inventory adjustments.

### Phase 4: Reports & Auditing
1. **Implement Cloud Reporting Endpoints (`/cloud/reports/...`).**
2. **Implement DB Audit Triggers / Audit Service for `audit_logs`.**
