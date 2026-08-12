import { StatTile } from '@/globalComponents/StatTile';
import { DollarSign, ShoppingBag, Store, Users } from 'lucide-react';
import type { DashboardMetrics } from '@/hooks/useDashboard';

export interface DashboardStatGridProps {
  metrics: DashboardMetrics;
  loading?: boolean;
}

export function DashboardStatGrid({ metrics, loading }: DashboardStatGridProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <StatTile
        label="Total Sales (Today)"
        value={metrics.totalSales}
        icon={<DollarSign size={20} strokeWidth={1.5} />}
        subtext="+12% from yesterday"
        loading={loading}
      />
      <StatTile
        label="Total Orders"
        value={metrics.totalOrders}
        icon={<ShoppingBag size={20} strokeWidth={1.5} />}
        subtext="34 open / held"
        loading={loading}
      />
      <StatTile
        label="Active Branches"
        value={metrics.activeBranches}
        icon={<Store size={20} strokeWidth={1.5} />}
        subtext="Operational"
        loading={loading}
      />
      <StatTile
        label="Total Employees"
        value={metrics.totalEmployees}
        icon={<Users size={20} strokeWidth={1.5} />}
        subtext="Across all branches"
        loading={loading}
      />
    </div>
  );
}

export default DashboardStatGrid;
