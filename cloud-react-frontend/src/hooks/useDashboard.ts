import { useCallback, useState } from 'react';
import { branchesApi, employeesApi, productsApi, reportsApi } from '@/services/resources';
import { extractErrorMessage } from '@/services/api';
import { useAuth } from './useAuth';
import { useResource } from './useResource';
import type { InventoryReport, SalesReport } from '@/types/domain';

export interface DashboardCounts {
  branches: number;
  employees: number;
  products: number;
}

export interface DashboardSnapshot {
  sales: SalesReport | null;
  inventory: InventoryReport | null;
  counts: DashboardCounts;
  /** Endpoints that failed, so the UI can degrade honestly instead of showing zeros. */
  failed: string[];
}

const EMPTY: DashboardSnapshot = {
  sales: null,
  inventory: null,
  counts: { branches: 0, employees: 0, products: 0 },
  failed: [],
};

/**
 * Aggregates the dashboard from the report endpoints plus entity counts.
 * There is no single summary endpoint, so this fans out and tolerates partial
 * failure: one broken report must not blank the whole page.
 */
async function loadSnapshot(): Promise<DashboardSnapshot> {
  const [sales, inventory, branches, employees, products] = await Promise.allSettled([
    reportsApi.sales(),
    reportsApi.inventory(),
    branchesApi.list(),
    employeesApi.list(),
    productsApi.list(),
  ]);

  const failed: string[] = [];
  if (sales.status === 'rejected') failed.push('sales report');
  if (inventory.status === 'rejected') failed.push('inventory report');
  if (branches.status === 'rejected') failed.push('branches');
  if (employees.status === 'rejected') failed.push('employees');
  if (products.status === 'rejected') failed.push('products');

  return {
    sales: sales.status === 'fulfilled' ? sales.value : null,
    inventory: inventory.status === 'fulfilled' ? inventory.value : null,
    counts: {
      branches: branches.status === 'fulfilled' ? branches.value.length : 0,
      employees: employees.status === 'fulfilled' ? employees.value.length : 0,
      products: products.status === 'fulfilled' ? products.value.length : 0,
    },
    failed,
  };
}

export function useDashboard() {
  const { user } = useAuth();
  const loader = useCallback(() => loadSnapshot(), []);
  const { data, loading, error, reload } = useResource<DashboardSnapshot>(loader, EMPTY);
  const [refreshing, setRefreshing] = useState(false);

  const refresh = async () => {
    setRefreshing(true);
    try {
      await reload();
    } catch (err) {
      // reload() already captures the message into `error`.
      void extractErrorMessage(err);
    } finally {
      setRefreshing(false);
    }
  };

  const lowStockItems = (data.inventory?.items ?? []).filter((i) => i.is_low_stock);

  return {
    user,
    loading,
    refreshing,
    error,
    refresh,
    sales: data.sales,
    inventory: data.inventory,
    counts: data.counts,
    failed: data.failed,
    lowStockItems,
  };
}

export default useDashboard;
