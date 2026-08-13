import { TrendingUp, ShoppingBag, Store, Users, Package, Undo2 } from 'lucide-react';
import { StatTile } from '@/globalComponents/StatTile';
import { formatMoney } from '@/lib/format';
import type { SalesReport } from '@/types/domain';
import type { DashboardCounts } from '@/hooks/useDashboard';

export interface DashboardStatGridProps {
  sales: SalesReport | null;
  counts: DashboardCounts;
  loading?: boolean;
}

export function DashboardStatGrid({ sales, counts, loading }: DashboardStatGridProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <StatTile
        label="Total sales"
        value={sales ? `$${formatMoney(sales.total_sales_amount)}` : '—'}
        icon={<TrendingUp size={20} strokeWidth={1.5} />}
        subtext={sales ? `Average order $${formatMoney(sales.average_order_value)}` : 'No sales data'}
        loading={loading}
      />
      <StatTile
        label="Orders"
        value={sales ? sales.total_orders_count : '—'}
        icon={<ShoppingBag size={20} strokeWidth={1.5} />}
        subtext={sales ? `${sales.refunded_orders_count} refunded` : 'No sales data'}
        loading={loading}
      />
      <StatTile
        label="Refunded"
        value={sales ? `$${formatMoney(sales.total_refunded_amount)}` : '—'}
        icon={<Undo2 size={20} strokeWidth={1.5} />}
        subtext="Across all branches"
        loading={loading}
      />
      <StatTile
        label="Branches"
        value={counts.branches}
        icon={<Store size={20} strokeWidth={1.5} />}
        subtext="Configured locations"
        loading={loading}
      />
      <StatTile
        label="Employees"
        value={counts.employees}
        icon={<Users size={20} strokeWidth={1.5} />}
        subtext="On the payroll"
        loading={loading}
      />
      <StatTile
        label="Products"
        value={counts.products}
        icon={<Package size={20} strokeWidth={1.5} />}
        subtext="In the catalogue"
        loading={loading}
      />
    </div>
  );
}

export default DashboardStatGrid;
