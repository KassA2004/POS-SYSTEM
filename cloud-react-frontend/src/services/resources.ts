import { api } from './api';
import type {
  Branch,
  BranchCreate,
  BranchUpdate,
  BranchEmployee,
  BranchEmployeeAssign,
  BranchEmployeeUpdate,
  Employee,
  EmployeeCreate,
  EmployeeUpdate,
  InventoryRecord,
  InventoryReport,
  Permission,
  Product,
  ProductCreate,
  ProductDetail,
  ProductRecipe,
  ProductRecipeCreate,
  ProductRecipeUpdate,
  ProductUpdate,
  Role,
  RoleCreate,
  RoleUpdate,
  SalesReport,
  WarehouseItem,
  WarehouseItemCreate,
  WarehouseItemUpdate,
} from '@/types/domain';

// --- Branches -------------------------------------------------------------
export const branchesApi = {
  list: () => api.get<Branch[]>('/branches/').then((r) => r.data),
  get: (id: number) => api.get<Branch>(`/branches/${id}`).then((r) => r.data),
  create: (data: BranchCreate) => api.post<Branch>('/branches/', data).then((r) => r.data),
  update: (id: number, data: BranchUpdate) => api.put<Branch>(`/branches/${id}`, data).then((r) => r.data),
  remove: (id: number) => api.delete(`/branches/${id}`).then((r) => r.data),
};

// --- Employees ------------------------------------------------------------
export const employeesApi = {
  list: () => api.get<Employee[]>('/employees/').then((r) => r.data),
  get: (id: number) => api.get<Employee>(`/employees/${id}`).then((r) => r.data),
  create: (data: EmployeeCreate) => api.post<Employee>('/employees/', data).then((r) => r.data),
  update: (id: number, data: EmployeeUpdate) => api.put<Employee>(`/employees/${id}`, data).then((r) => r.data),
  remove: (id: number) => api.delete(`/employees/${id}`).then((r) => r.data),
};

// --- Roles & permissions --------------------------------------------------
export const rolesApi = {
  list: () => api.get<Role[]>('/roles/').then((r) => r.data),
  // NOTE: /roles/permissions must stay above /roles/{id} on the backend or the
  // literal path would be swallowed by the int path param.
  permissions: () => api.get<Permission[]>('/roles/permissions').then((r) => r.data),
  get: (id: number) => api.get<Role>(`/roles/${id}`).then((r) => r.data),
  create: (data: RoleCreate) => api.post<Role>('/roles/', data).then((r) => r.data),
  update: (id: number, data: RoleUpdate) => api.put<Role>(`/roles/${id}`, data).then((r) => r.data),
  remove: (id: number) => api.delete(`/roles/${id}`).then((r) => r.data),
};

// --- Branch <-> employee assignments -------------------------------------
export const assignmentsApi = {
  list: (params?: { employee_id?: number; branch_id?: number; include_removed?: boolean }) =>
    api.get<BranchEmployee[]>('/branch-employees', { params }).then((r) => r.data),
  assign: (branchId: number, data: BranchEmployeeAssign) =>
    api.post<BranchEmployee>(`/branches/${branchId}/assign`, data).then((r) => r.data),
  update: (assignmentId: number, data: BranchEmployeeUpdate) =>
    api.put<BranchEmployee>(`/branch-employees/${assignmentId}`, data).then((r) => r.data),
  remove: (assignmentId: number) => api.delete(`/branch-employees/${assignmentId}`).then((r) => r.data),
};

// --- Warehouse items (ingredients) ---------------------------------------
export const warehouseItemsApi = {
  list: () => api.get<WarehouseItem[]>('/warehouse-items/').then((r) => r.data),
  get: (id: number) => api.get<WarehouseItem>(`/warehouse-items/${id}`).then((r) => r.data),
  create: (data: WarehouseItemCreate) => api.post<WarehouseItem>('/warehouse-items/', data).then((r) => r.data),
  update: (id: number, data: WarehouseItemUpdate) =>
    api.put<WarehouseItem>(`/warehouse-items/${id}`, data).then((r) => r.data),
  remove: (id: number) => api.delete(`/warehouse-items/${id}`).then((r) => r.data),
};

// --- Inventory (schema-owner gated, lives under the /pos prefix) ----------
export const inventoryApi = {
  list: () => api.get<InventoryRecord[]>('/pos/inventory/').then((r) => r.data),
  get: (itemId: number) => api.get<InventoryRecord>(`/pos/inventory/${itemId}`).then((r) => r.data),
  initialise: (data: InventoryRecord) => api.post<InventoryRecord>('/pos/inventory/', data).then((r) => r.data),
  setQuantity: (itemId: number, quantity: number) =>
    api.put<InventoryRecord>(`/pos/inventory/${itemId}`, { quantity }).then((r) => r.data),
};

// --- Products & recipes ---------------------------------------------------
export const productsApi = {
  list: () => api.get<Product[]>('/products/').then((r) => r.data),
  get: (id: number) => api.get<ProductDetail>(`/products/${id}`).then((r) => r.data),
  create: (data: ProductCreate) => api.post<Product>('/products/', data).then((r) => r.data),
  update: (id: number, data: ProductUpdate) => api.put<Product>(`/products/${id}`, data).then((r) => r.data),
  remove: (id: number) => api.delete(`/products/${id}`).then((r) => r.data),

  addRecipe: (productId: number, data: ProductRecipeCreate) =>
    api.post<ProductRecipe>(`/products/${productId}/recipes`, data).then((r) => r.data),
  updateRecipe: (productId: number, recipeId: number, data: ProductRecipeUpdate) =>
    api.put<ProductRecipe>(`/products/${productId}/recipes/${recipeId}`, data).then((r) => r.data),
  removeRecipe: (productId: number, recipeId: number) =>
    api.delete(`/products/${productId}/recipes/${recipeId}`).then((r) => r.data),
};

// --- Reports --------------------------------------------------------------
export const reportsApi = {
  sales: (params?: { branch_id?: number; employee_id?: number; start_date?: string; end_date?: string }) =>
    api.get<SalesReport>('/cloud/reports/sales', { params }).then((r) => r.data),
  inventory: (lowStockOnly = false) =>
    api
      .get<InventoryReport>('/cloud/reports/inventory', { params: { low_stock_only: lowStockOnly } })
      .then((r) => r.data),
};
