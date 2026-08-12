import { DataTable, type Column } from '@/globalComponents/DataTable';
import { StatusBadge } from '@/globalComponents/StatusBadge';
import { CircleCheck, TriangleAlert, Info, CircleAlert } from 'lucide-react';
import type { ActivityRow } from '@/hooks/useDashboard';

export interface DashboardOverviewTableProps {
  activities: ActivityRow[];
  loading?: boolean;
}

const statusMap = {
  success: { variant: 'success' as const, icon: <CircleCheck size={14} strokeWidth={2} />, label: 'Normal' },
  warning: { variant: 'warning' as const, icon: <TriangleAlert size={14} strokeWidth={2} />, label: 'Warning' },
  info:    { variant: 'info' as const, icon: <Info size={14} strokeWidth={2} />, label: 'Info' },
  danger:  { variant: 'danger' as const, icon: <CircleAlert size={14} strokeWidth={2} />, label: 'Alert' },
};

export function DashboardOverviewTable({ activities, loading }: DashboardOverviewTableProps) {
  const columns: Column<ActivityRow>[] = [
    {
      key: 'description',
      header: 'System Event / Activity',
      render: (row) => <span className="font-medium text-ink-primary">{row.description}</span>,
    },
    {
      key: 'status',
      header: 'Status Signal',
      render: (row) => {
        const config = statusMap[row.status];
        return (
          <StatusBadge variant={config.variant} icon={config.icon}>
            {config.label}
          </StatusBadge>
        );
      },
    },
    {
      key: 'timestamp',
      header: 'Time',
      align: 'right',
      render: (row) => <span className="text-body-sm text-ink-tertiary tabular-nums">{row.timestamp}</span>,
    },
  ];

  return <DataTable columns={columns} data={activities} loading={loading} emptyText="No recent activities logged." />;
}

export default DashboardOverviewTable;
