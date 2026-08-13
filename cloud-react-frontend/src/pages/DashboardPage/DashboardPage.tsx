import { RotateCw } from 'lucide-react';
import { AppShell } from '@/globalComponents/AppShell';
import { Button } from '@/globalComponents/Button';
import { Alert } from '@/globalComponents/Alert';
import { useDashboard } from '@/hooks/useDashboard';
import { DashboardStatGrid } from './components/DashboardStatGrid';
import { LowStockPanel } from './components/LowStockPanel';
import { SalesByBranchPanel } from './components/SalesByBranchPanel';

export function DashboardPage() {
  const { user, loading, refreshing, error, refresh, sales, counts, failed, lowStockItems } = useDashboard();

  return (
    <AppShell
      title="Dashboard"
      actions={
        <Button
          variant="secondary"
          icon={<RotateCw size={16} strokeWidth={1.5} />}
          onClick={refresh}
          loading={refreshing}
        >
          Refresh
        </Button>
      }
    >
      <div className="space-y-8">
        {error && <Alert variant="danger" title="Could not load the dashboard">{error}</Alert>}

        {!error && failed.length > 0 && (
          <Alert variant="warning" title="Some data could not be loaded">
            The following did not respond: {failed.join(', ')}. Everything else on this page is current.
          </Alert>
        )}

        <section className="space-y-4">
          <div className="flex items-baseline justify-between gap-4">
            <h2 className="text-h3 font-semibold text-ink-primary">Overview</h2>
            <p className="text-caption text-ink-tertiary">
              Workspace <span className="font-mono text-ink-secondary">{user?.schema_name}</span>
            </p>
          </div>
          <DashboardStatGrid sales={sales} counts={counts} loading={loading} />
        </section>

        <div className="grid gap-6 lg:grid-cols-2">
          <SalesByBranchPanel sales={sales} loading={loading} />
          <LowStockPanel items={lowStockItems} loading={loading} />
        </div>
      </div>
    </AppShell>
  );
}

export default DashboardPage;
