import { type ReactNode, useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  Zap,
  Building2,
  Sun,
  Moon,
  LogOut,
  LayoutDashboard,
  Store,
  Users,
  Package,
  Boxes,
  ShieldCheck,
  Menu,
  X,
  CircleUser,
} from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { useTheme } from '@/hooks/useTheme';
import { cn } from '@/lib/cn';

export interface AppShellProps {
  children: ReactNode;
  title?: string;
  actions?: ReactNode;
}

const navItems = [
  { label: 'Overview', items: [{ name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard }] },
  {
    label: 'Organisation',
    items: [
      { name: 'Branches', path: '/branches', icon: Store },
      { name: 'Employees', path: '/employees', icon: Users },
      { name: 'Roles', path: '/roles', icon: ShieldCheck },
    ],
  },
  {
    label: 'Catalogue',
    items: [
      { name: 'Ingredients', path: '/ingredients', icon: Boxes },
      { name: 'Products', path: '/products', icon: Package },
    ],
  },
];

export function AppShell({ children, title, actions }: AppShellProps) {
  const { user, logout } = useAuth();
  const { isDark, toggleTheme } = useTheme();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-canvas flex flex-col">
      {/* Topbar */}
      <header className="h-14 bg-surface border-b border-border-subtle sticky top-0 z-30 flex items-center justify-between px-4 lg:px-6">
        <div className="flex items-center gap-3">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="lg:hidden p-1.5 rounded-md text-ink-secondary hover:bg-surface-hover"
            aria-label="Toggle navigation menu"
          >
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>

          <div className="flex items-center gap-2 font-bold text-lead text-ink-primary select-none">
            <div className="w-7 h-7 rounded-md bg-ink-primary text-ink-inverse flex items-center justify-center">
              <Zap size={16} strokeWidth={2} />
            </div>
            <span>POS Cloud</span>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <button
            onClick={toggleTheme}
            className="p-2 rounded-md text-ink-secondary hover:bg-surface-hover hover:text-ink-primary transition-colors cursor-pointer"
            aria-label="Toggle dark mode"
          >
            {isDark ? <Sun size={18} strokeWidth={1.5} /> : <Moon size={18} strokeWidth={1.5} />}
          </button>

          <div className="hidden sm:flex items-center gap-2 text-body-sm text-ink-secondary bg-surface-sunken px-3 py-1.5 rounded-md border border-border-subtle">
            <Building2 size={16} strokeWidth={1.5} />
            <span className="font-medium text-ink-primary">{user?.schema_name || 'Tenant Workspace'}</span>
          </div>

          <div className="flex items-center gap-3 border-l border-border-subtle pl-4">
            <div className="hidden md:flex flex-col text-right">
              <span className="text-body-sm font-medium text-ink-primary">{user?.email}</span>
              <span className="text-caption text-ink-tertiary">{user?.role}</span>
            </div>
            <div className="w-8 h-8 rounded-full bg-surface-sunken border border-border-subtle flex items-center justify-center text-ink-secondary">
              <CircleUser size={20} strokeWidth={1.5} />
            </div>
            <button
              onClick={handleLogout}
              className="p-1.5 rounded-md text-ink-secondary hover:text-danger-fg hover:bg-danger-bg transition-colors cursor-pointer"
              title="Sign out"
            >
              <LogOut size={18} strokeWidth={1.5} />
            </button>
          </div>
        </div>
      </header>

      <div className="flex-1 flex">
        {/* Sidebar Navigation */}
        <aside
          className={cn(
            'w-60 bg-surface border-r border-border-subtle flex flex-col fixed inset-y-14 left-0 z-20 transition-transform duration-200 lg:static lg:translate-x-0',
            sidebarOpen ? 'translate-x-0' : '-translate-x-full'
          )}
        >
          <nav className="flex-1 p-3 space-y-6 overflow-y-auto">
            {navItems.map((group) => (
              <div key={group.label} className="space-y-1">
                <div className="px-3 text-micro uppercase tracking-[0.04em] font-semibold text-ink-tertiary">
                  {group.label}
                </div>
                {group.items.map((item) => (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    onClick={() => setSidebarOpen(false)}
                    className={({ isActive }) =>
                      cn(
                        'flex items-center gap-3 px-3 py-2 rounded-md text-body font-medium transition-colors',
                        isActive
                          ? 'bg-surface-sunken text-ink-primary font-semibold border-l-2 border-ink-primary'
                          : 'text-ink-secondary hover:bg-surface-hover hover:text-ink-primary'
                      )
                    }
                  >
                    <item.icon size={18} strokeWidth={1.5} />
                    <span>{item.name}</span>
                  </NavLink>
                ))}
              </div>
            ))}
          </nav>
        </aside>

        {/* Backdrop for mobile navigation */}
        {sidebarOpen && (
          <div
            onClick={() => setSidebarOpen(false)}
            className="fixed inset-0 top-14 bg-black/40 z-10 lg:hidden"
          />
        )}

        {/* Main Content Area */}
        <main className="flex-1 max-w-[1440px] w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {(title || actions) && (
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-border-subtle mb-6">
              {title && <h1 className="text-h1 font-bold text-ink-primary tracking-[-0.02em]">{title}</h1>}
              {actions && <div className="flex items-center gap-3">{actions}</div>}
            </div>
          )}
          {children}
        </main>
      </div>
    </div>
  );
}

export default AppShell;
