import { CircleCheck, TriangleAlert } from 'lucide-react';
import { Card } from '@/globalComponents/Card';
import { DataTable, type Column } from '@/globalComponents/DataTable';
import { EmptyState } from '@/globalComponents/EmptyState';
import { StatusBadge } from '@/globalComponents/StatusBadge';
import { formatQuantity } from '@/lib/format';
import type { InventoryReportItem } from '@/types/domain';

export interface LowStockPanelProps {
  items: InventoryReportItem[];
  loading?: boolean;
}

export function LowStockPanel({ items, loading }: LowStockPanelProps) {
  const columns: Column<InventoryReportItem>[] = [
    {
      key: 'name',
      header: 'Ingredient',
      render: (row) => <span className="font-medium text-ink-primary">{row.name}</span>,
    },
    {
      key: 'current_stock',
      header: 'In stock',
      align: 'right',
      render: (row) => (
        <span className="tabular-nums text-warning-fg">
          {formatQuantity(row.current_stock)} <span className="text-ink-tertiary">{row.unit_of_measure}</span>
        </span>
      ),
    },
    {
      key: 'minimum_stock',
      header: 'Minimum',
      align: 'right',
      render: (row) => (
        <span className="tabular-nums text-ink-secondary">{formatQuantity(row.minimum_stock)}</span>
      ),
    },
  ];

  return (
    <Card
      title="Low stock"
      actions={
        items.length > 0 ? (
          <StatusBadge variant="warning" icon={<TriangleAlert size={14} strokeWidth={2} />}>
            {items.length}
          </StatusBadge>
        ) : undefined
      }
      bodyClassName="p-0"
    >
      {!loading && items.length === 0 ? (
        <EmptyState
          icon={<CircleCheck size={24} strokeWidth={1.5} />}
          title="Everything is above minimum"
          message="No ingredient has fallen to its low-stock threshold."
        />
      ) : (
        <DataTable columns={columns} data={items} loading={loading} emptyText="No low stock items." />
      )}
    </Card>
  );
}

export default LowStockPanel;
