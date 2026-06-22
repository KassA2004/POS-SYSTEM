# Enterprise POS & Business Management System — Design Phase Plan

**Stack:** React + TypeScript + Vite · FastAPI (Python, async) · PostgreSQL (raw SQL / lightweight query builder, no heavy ORM)
**Scope:** Multi-branch from day one
**Goal:** Resume-grade deliverable + deep learning vehicle for concurrency control, transaction isolation, and audit-grade data integrity

---

## 1. Why This Order Matters

A POS system has a brutal dependency chain: you cannot design the sales screen without knowing the inventory model. You cannot design inventory without knowing how branches share (or don't share) stock. You cannot design RBAC without knowing every action that needs gating. If you design top-down (UI first) you'll redesign your schema three times. If you design bottom-up correctly once, everything above it slots in.

So this plan moves in this order:

1. **Domain model** — decide the hard conceptual questions before any artifact is drawn
2. **Entity Relationship Diagram (ERD)** — the foundation everything else depends on
3. **Permission matrix (RBAC)** — depends on knowing every entity and action
4. **Core workflows** — depends on schema + permissions existing
5. **Screen/dashboard layouts** — depends on workflows being settled
6. **Audit logging strategy** — depends on knowing every mutable table
7. **Scalability / future-phase notes** — last, so it doesn't distort the MVP

Each artifact will be its own document/file so you can version and reference them independently.

---

## 2. Domain Decisions — LOCKED

These are the architecturally expensive questions, answered up front so the schema only gets built once.

### 2.1 Inventory model — **Shared central warehouse per tenant, branches draw from it**
- Inventory is keyed by `(tenant_id, product_id)` at the warehouse level, not `(branch_id, product_id)`. Branches do not hold independent stock; they consume against the tenant's shared warehouse balance.
- This is also the entire reason the concurrency-control problem exists: two branches selling the last unit of the same product at the same instant are now contending for the *same row*, not two separate rows. That's the scenario the locking strategy (Section 7 artifact) is built around.
- Stock transfers are *intra-tenant, inter-branch* in the sense of fulfillment/logistics tracking (which branch a delivery is headed to), but the authoritative stock count lives at the warehouse level, scoped to the tenant.

### 2.2 Identity & tenancy model — **Multi-tenant**
- The platform can host multiple separate businesses ("tenants"). Every tenant-owned entity — branches, employees, roles, products, the warehouse itself, orders, audit logs — carries a `tenant_id`, enforced at the query layer (and reinforced by Postgres Row-Level Security in the concurrency/isolation spec).
- **Important boundary:** "shared warehouse" from 2.1 means shared *within* a tenant's branches — never shared across tenants. Two different businesses on the platform never see or draw from each other's stock.
- This raises the cost of nearly every other artifact (RBAC needs a tenant scope layer, audit logs need tenant_id on every row, every query needs a tenant filter) — but it's a deliberate, real piece of resume-grade complexity, not incidental scope creep.
- Open sub-question to settle when we build the ERD: does an employee belong to exactly one branch (within one tenant), or can they be scheduled across multiple branches of the same tenant? Defaulting to **one tenant, one primary branch, with optional cross-branch shift assignment** unless you say otherwise — flag it then if you want something different.

### 2.3 Recipe-level inventory — **In scope for Phase 1**
- Sellable products can be either: (a) directly mapped to a warehouse stock item (e.g., a bottled drink), or (b) a **recipe** — a product composed of N ingredient line items, each pointing to a warehouse stock item with a required quantity (e.g., Latte = Milk 200ml + Espresso Shot 18g + Cup 1ea).
- This means a single sale can trigger a multi-row stock deduction, all of which must happen atomically inside one locked transaction. If any ingredient is insufficient, the whole sale must fail cleanly — this is a direct, concrete instance of the "payment clears but inventory deduction fails" rollback scenario from your stack notes, and it's a stronger concurrency/transaction-isolation case study than single-row deduction would have been.
- This also means the Inventory Management artifact needs a `recipe_items` (or `product_components`) table from the start, not bolted on later.

### 2.4 Money handling
- Single currency for Phase 1; schema should not be hostile to multi-currency later (a `currency_code` column at the tenant level is cheap insurance, full multi-currency math is deferred).
- All monetary columns use Postgres `NUMERIC`, never `FLOAT` — non-negotiable for a financial system.

### 2.5 Order lifecycle
- Canonical state machine to formalize in the Sales workflow artifact: `open → held → paid → closed`, with `voided` and `refunded` as terminal branches reachable only from `paid`/`closed`. "Hold Order," "Resume Order," "Void," and "Refund" are transitions on this state machine, not independent flags — this keeps the order's status always unambiguous and auditable.

### 2.6 Concurrency boundary — confirmed
- Lock contention happens at the **warehouse stock row**, scoped by `(tenant_id, product_id)` — and, per 2.3, potentially across *several* such rows in a single recipe-based sale. This is the central case the concurrency & isolation artifact is designed around.

---

## 3. Design Phase Deliverables (Artifacts)

Each of these becomes its own document. Listed in build order, with what each one depends on.

| # | Artifact | Depends On | Output Format |
|---|----------|-----------|----------------|
| 1 | **Domain Decisions Record** | Section 2 answers | Short doc — the "why" behind schema choices |
| 2 | **Entity Relationship Diagram** | #1 | Diagram + full entity/field reference doc |
| 3 | **Permission Matrix (RBAC)** | #2 | Table: roles × permissions × scope (own-branch / all-branch) |
| 4 | **Core Workflows** (Auth, Sales/Order lifecycle, Shift open/close, Inventory movement, Refund/Void, Multi-branch transfer) | #2, #3 | Flow diagrams, one per workflow |
| 5 | **Audit Logging Strategy** | #2 | Trigger/table design doc — ties to your DB-level audit goal |
| 6 | **Screen Layouts** (POS sales screen, Manager dashboard, Admin dashboard) | #4 | Wireframe-level mockups |
| 7 | **Concurrency & Transaction Isolation Spec** | #1, #2 | Technical doc — locking strategy per operation, isolation level per transaction type |
| 8 | **Scalability & Future-Phase Notes** | All above | Short doc mapping "Future Expansion" spec items to schema hooks already in place |

Artifacts 1–4 are the ones that gate everything else — nothing downstream can be designed correctly without them. I'd treat 5 and 7 as the "learning value" core, since that's where the pessimistic locking, isolation levels, and triggers actually live. 6 and 8 are lower-risk and can move fast once the others are solid.

---

## 4. Explicit Phase 1 Scope (MVP)

To keep this buildable, here's what's **in** for the first full build pass vs. **designed-for-but-deferred**.

### In scope for Phase 1
- Multi-branch structure (create/edit/disable branch)
- Employee management + RBAC with custom roles
- Authentication (username/password + PIN login; RFID/QR deferred but schema-compatible)
- Inventory: products, stock levels, adjustments, movement, low-stock alerts
- Inventory concurrency control (the core learning objective)
- POS sales screen: product grid, order creation, hold/resume, payment (cash/card/digital wallet), receipts
- Shift management: open/close, cash reconciliation
- Voids & refunds with approval requirements
- Audit logging (database-level, via triggers)
- Core reporting: sales, inventory, shift/cash reconciliation
- Multi-branch stock transfer

### Designed-for-but-deferred (schema accommodates, full workflow/UI doesn't get built yet)
- Table management (restaurant mode)
- Purchase orders with full approval chain
- Supplier management
- Customer loyalty/rewards program
- Split bill / merge orders
- Discount approval workflows beyond a basic flag

### Out of scope (Phase 1 schema should not actively block these, nothing more)
- Everything under "Future Expansion Features" in your spec (online ordering, kiosk, KDS, AI forecasting, multi-country, franchise management)

This split is what artifact #8 (Scalability Notes) will formally document — i.e., "here's where the hooks are for X even though X isn't built."

---

## 5. Suggested Working Order

1. Lock domain decisions (Section 2) — fast conversation, high leverage
2. Build the ERD + entity reference
3. Build the permission matrix
4. Build core workflows (start with Sales/Order lifecycle — it touches the most entities)
5. Write the concurrency & isolation spec alongside the inventory and sales workflows, since they're really one design problem
6. Write the audit logging strategy
7. Screen layouts
8. Scalability notes

---

## Next Step

Domain decisions are locked. The next artifact is the **Entity Relationship Diagram** — it's the first place the multi-tenant + shared-warehouse + recipe-inventory decisions all become concrete tables and foreign keys. I'll build that next: full entity list, fields, relationships, and the tenant-scoping pattern applied consistently across every table.
