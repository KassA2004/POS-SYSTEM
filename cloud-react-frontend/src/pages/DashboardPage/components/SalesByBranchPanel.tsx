import { TrendingUp } from 'lucide-react';
import { Card } from '@/globalComponents/Card';
import { DataTable, type Column } from '@/globalComponents/DataTable';
import { EmptyState } from '@/globalComponents/EmptyState';
import { formatMoney } from '@/lib/format';
import type { BranchSalesBreakdown, SalesReport } from '@/types/domain';

export interface SalesByBranchPanelProps {
  sales: SalesReport | null;
  loading?: boolean;
}

export function SalesByBranchPanel({ sales, loading }: SalesByBranchPanelProps) {
  const rows = sales?.by_branch ?? [];

  const columns: Column<BranchSalesBreakdown>[] = [
    {
      key: 'branch_name',
      header: 'Branch',
      render: (row) => <span className="font-medium text-ink-primary">{row.branch_name}</span>,
    },
    {
      key: 'orders_count',
      header: 'Orders',
      align: 'right',
      render: (row) => <span className="tabular-nums text-ink-secondary">{row.orders_count}</span>,
    },
    {
      key: 'sales_amount',
      header: 'Sales',
      align: 'right',
      render: (row) => (
        <span className="tabular-nums text-ink-primary">
          <span className="text-ink-tertiary mr-0.5">$</span>
          {formatMoney(row.sales_amount)}
        </span>
      ),
    },
  ];

  return (
    <Card title="Sales by branch" bodyClassName="p-0">
      {!loading && rows.length === 0 ? (
        <EmptyState
          icon={<TrendingUp size={24} strokeWidth={1.5} />}
          title="No sales recorded"
          message="Sales appear here once orders are rung up on a POS terminal."
        />
      ) : (
        <DataTable columns={columns} data={rows} loading={loading} emptyText="No sales recorded." />
      )}
    </Card>
  );
}

export default SalesByBranchPanel;
