import { useState, useEffect } from 'react';
import { useAuth } from './useAuth';

export interface DashboardMetrics {
  totalSales: string;
  totalOrders: number;
  activeBranches: number;
  totalEmployees: number;
}

export interface ActivityRow {
  id: string;
  description: string;
  timestamp: string;
  status: 'success' | 'warning' | 'info' | 'danger';
}

export function useDashboard() {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [metrics, setMetrics] = useState<DashboardMetrics>({
    totalSales: '$0.00',
    totalOrders: 0,
    activeBranches: 1,
    totalEmployees: 1,
  });
  const [recentActivities, setRecentActivities] = useState<ActivityRow[]>([]);

  useEffect(() => {
    let isMounted = true;
    const fetchDashboardData = async () => {
      setLoading(true);
      try {
        // Mock / placeholder data bootstrapping until analytics endpoints are expanded
        if (isMounted) {
          setMetrics({
            totalSales: '$12,450.00',
            totalOrders: 342,
            activeBranches: 2,
            totalEmployees: 8,
          });
          setRecentActivities([
            { id: '1', description: 'Branch "Downtown Coffee" opened shift #104', timestamp: '10 mins ago', status: 'success' },
            { id: '2', description: 'Low stock threshold reached for Espresso Beans (1.2 kg left)', timestamp: '45 mins ago', status: 'warning' },
            { id: '3', description: 'New employee assigned to Branch "Uptown Cafe"', timestamp: '2 hours ago', status: 'info' },
            { id: '4', description: 'Order #1092 voided by Manager', timestamp: '3 hours ago', status: 'danger' },
          ]);
        }
      } catch (err) {
        console.error('Failed to fetch dashboard data:', err);
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    fetchDashboardData();
    return () => {
      isMounted = false;
    };
  }, []);

  return {
    user,
    loading,
    metrics,
    recentActivities,
  };
}

export default useDashboard;
