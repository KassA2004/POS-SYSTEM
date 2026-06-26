# Permission Matrix and RBAC Architecture Specification

## 1. Purpose

This document defines the Role-Based Access Control and authentication architecture for a multi-tenant Point of Sale ecosystem. It establishes strict security boundaries between the Cloud Back-Office used by administrators and the POS Application used by employees.

The system is designed around three core principles: strict tenant isolation, support for complex multi-branch organizations, and a permission system based on least privilege.

## 2. System Architecture and Boundaries

The system is divided into two primary application environments with distinct purposes and access rules.

### Cloud Back-Office

This is a web-based administrative dashboard.

It is used by super administrators and tenant administrators.

Its responsibilities include:

* Tenant provisioning and management
* Branch management
* Role creation and permission configuration
* Employee management
* Reporting and analytics

### POS Application

This is a client-side application installed on physical POS hardware.

It is used by employees for day-to-day operations.

Its responsibilities include:

* Processing orders
* Managing cash operations
* Handling transactions
* Executing shift-level operational tasks

## 3. Identity and Authentication Model

### Super Admin

Super admins are the top-level system operators responsible for managing the entire platform.

They can create, suspend, and manage tenants.

They authenticate using centralized system-level credentials that are not part of any tenant scope.

### Tenant Admin

Tenant admins represent a single business entity operating within the system.

They have full control over their tenant environment, including branches, roles, and employees.

They access the Cloud Back-Office using a username and password issued at tenant creation.

Tenant admins operate with implicit full authorization inside their tenant and do not require granular role assignments.

### Employee

Employees are operational users of the POS Application.

They authenticate using an auto-generated numeric ID and an optional PIN code.

If no PIN is set, access can be granted using the ID alone.

Employees have no access to the Cloud Back-Office.

## 4. Multi-Tenant Isolation Rules

Each tenant exists as a fully isolated data environment.

No data, authentication context, or operational structure can be shared between tenants.

Employees, branches, roles, and permissions are strictly scoped to their owning tenant and cannot be accessed externally under any condition.


## 5. Role System and Permission Design

Roles are dynamically created by tenant administrators.

The system does not provide predefined roles.

Roles act as containers for permissions.

Permissions are always assigned to roles.

Employees never receive direct permissions.

Instead, employees inherit permissions through role assignments.

## 6. Branch Role Assignment Model

The system uses a three-way relationship between employee, branch, and role.

An employee may exist across multiple branches within the same tenant.

However, for each branch, the employee can only hold one role.

This allows flexible real-world structures where the same person can have different responsibilities depending on location.

When an employee logs into a specific branch, the system resolves their permissions exclusively based on the role assigned for that branch.

If no role exists for that branch, access is denied.

## 7. Permission Model

Permissions follow a structured domain action naming convention.

Order permissions:
order.preview allows viewing order details without processing a transaction
order.void allows cancellation of active orders
order.refund allows reversing completed transactions
order.discount allows applying manual discounts

Sales permissions:
sales.read_shift allows viewing current shift metrics
sales.read_history allows viewing historical sales data

Cash permissions:
cash.open_drawer allows triggering the cash drawer without a sale
cash.pay_in allows recording manual cash additions
cash.pay_out allows recording manual cash withdrawals

These permissions are evaluated dynamically by backend business logic.


## 8. Session Management and Security Lifecycle

Sessions are bound to a specific POS device instance.

When an employee logs in, a session token is issued containing branch-specific authorization data.

Sessions are immediately invalidated when:

* The user explicitly logs out
* The POS application closes or crashes
* The device loses power or restarts

On restart, authentication must be revalidated using ID and PIN.

The system periodically refreshes permission data from the backend to ensure changes in roles are reflected in active sessions.


## 9. Edge Cases and System Constraints

If an employee account is created without a PIN, the system must display a warning to administrators when assigning sensitive roles.

If an employee attempts to access a branch they are not assigned to, authentication must be rejected with an access denied response.

If a role is deleted while still assigned to active employees, the system must block the deletion to prevent invalid authorization states.
