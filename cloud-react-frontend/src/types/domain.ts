/**
 * Domain types mirroring the FastAPI Pydantic schemas in pos-engine/app/models/.
 *
 * Money and quantity columns are NUMERIC in Postgres and FastAPI serialises
 * them as JSON *strings* ("4.50", "10.000"), not numbers. They are typed
 * `Decimalish` so callers are forced through toNumber()/formatMoney() rather
 * than doing arithmetic on a string.
 */
import type { Decimalish } from '@/lib/format';

export type { Decimalish };

// --- Branches -------------------------------------------------------------
export interface Branch {
  id: number;
  name: string;
  address: string;
  is_active: boolean;
  created_at: string;
}

export interface BranchCreate {
  name: string;
  address: string;
  is_active: boolean;
}

export type BranchUpdate = Partial<BranchCreate>;

// --- Employees ------------------------------------------------------------
export interface Employee {
  id: number;
  name: string;
  date_of_birth?: string | null;
  phone?: string | null;
  created_at: string;
}

export interface EmployeeCreate {
  name: string;
  date_of_birth?: string | null;
  phone?: string | null;
  /** 4-8 digits. Write-only: EmployeeResponse never returns it. */
  pin?: string | null;
}

export type EmployeeUpdate = Partial<EmployeeCreate>;

// --- Roles & permissions --------------------------------------------------
export interface Permission {
  id: number;
  code: string;
  description?: string | null;
}

export interface Role {
  id: number;
  name: string;
  permissions: Permission[];
}

export interface RoleCreate {
  name: string;
  /** Backend requires at least one. */
  permission_ids: number[];
}

export interface RoleUpdate {
  name?: string;
  permission_ids?: number[];
}

// --- Branch <-> employee assignments -------------------------------------
export interface BranchEmployee {
  id: number;
  employee_id: number;
  branch_id: number;
  role_id?: number | null;
  assigned_at: string;
  removed_at?: string | null;
  employee_name?: string | null;
  branch_name?: string | null;
  role_name?: string | null;
}

export interface BranchEmployeeAssign {
  employee_id: number;
  role_id?: number | null;
}

export interface BranchEmployeeUpdate {
  role_id?: number | null;
  branch_id?: number | null;
}

// --- Warehouse items (ingredients / raw materials) ------------------------
export interface WarehouseItem {
  id: number;
  name: string;
  sku?: string | null;
  unit_of_measure: string;
  minimum_stock: Decimalish;
}

export interface WarehouseItemCreate {
  name: string;
  sku?: string | null;
  unit_of_measure: string;
  minimum_stock: Decimalish;
}

export type WarehouseItemUpdate = Partial<WarehouseItemCreate>;

// --- Inventory ------------------------------------------------------------
export interface InventoryRecord {
  warehouse_item_id: number;
  quantity: Decimalish;
}

// --- Products & recipes ---------------------------------------------------
export interface Product {
  id: number;
  name: string;
  price: Decimalish;
  is_recipe: boolean;
  direct_warehouse_item_id?: number | null;
  is_active: boolean;
  created_at: string;
}

export interface ProductRecipe {
  id: number;
  product_id: number;
  warehouse_item_id: number;
  quantity_required: Decimalish;
}

export interface ProductDetail extends Product {
  recipes: ProductRecipe[];
}

export interface ProductCreate {
  name: string;
  price: Decimalish;
  is_recipe: boolean;
  direct_warehouse_item_id?: number | null;
  is_active: boolean;
}

export type ProductUpdate = Partial<ProductCreate>;

export interface ProductRecipeCreate {
  warehouse_item_id: number;
  quantity_required: Decimalish;
}

export type ProductRecipeUpdate = Partial<ProductRecipeCreate>;

// --- Reports --------------------------------------------------------------
export interface BranchSalesBreakdown {
  branch_id: number;
  branch_name: string;
  sales_amount: Decimalish;
  orders_count: number;
}

export interface EmployeeSalesBreakdown {
  employee_id: number;
  employee_name: string;
  sales_amount: Decimalish;
  orders_count: number;
}

export interface SalesReport {
  total_sales_amount: Decimalish;
  total_orders_count: number;
  total_refunded_amount: Decimalish;
  refunded_orders_count: number;
  average_order_value: Decimalish;
  by_branch: BranchSalesBreakdown[];
  by_employee: EmployeeSalesBreakdown[];
}

export interface InventoryReportItem {
  warehouse_item_id: number;
  name: string;
  sku?: string | null;
  unit_of_measure: string;
  minimum_stock: Decimalish;
  current_stock: Decimalish;
  is_low_stock: boolean;
}

export interface InventoryReport {
  total_warehouse_items: number;
  low_stock_items_count: number;
  items: InventoryReportItem[];
}
