import { AppShell } from '@/globalComponents/AppShell';
import { Button } from '@/globalComponents/Button';
import { Plus, RotateCw } from 'lucide-react';
import { useDashboard } from '@/hooks/useDashboard';
import { DashboardStatGrid } from './components/DashboardStatGrid';
import { DashboardOverviewTable } from './components/DashboardOverviewTable';

export function DashboardPage() {
  const { user, loading, metrics, recentActivities } = useDashboard();

  return (
    <AppShell
      title="Dashboard Overview"
      actions={
        <>
          <Button variant="secondary" size="md" icon={<RotateCw size={16} strokeWidth={1.5} />}>
            Refresh
          </Button>
          <Button variant="primary" size="md" icon={<Plus size={16} strokeWidth={1.5} />}>
            New Branch
          </Button>
        </>
      }
    >
      <div className="space-y-8">
        <div className="bg-surface border border-border-default rounded-lg p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h2 className="text-h2 font-bold text-ink-primary">
              Active Tenant Schema: <span className="font-mono text-ink-secondary">{user?.schema_name || 'tenant_schema'}</span>
            </h2>
            <p className="text-body-sm text-ink-tertiary mt-1">
              Multi-tenant B2B POS Cloud Dashboard • Enterprise Tenant Isolation Active
            </p>
          </div>
        </div>

        <div className="space-y-4">
          <h3 className="text-h3 font-semibold text-ink-primary">Performance Metrics</h3>
          <DashboardStatGrid metrics={metrics} loading={loading} />
        </div>

        <div className="space-y-4">
          <h3 className="text-h3 font-semibold text-ink-primary">Recent Shift & System Audit Events</h3>
          <DashboardOverviewTable activities={recentActivities} loading={loading} />
        </div>
      </div>
    </AppShell>
  );
}

export default DashboardPage;
