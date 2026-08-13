import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from '@/context/AuthContext';
import { ToastProvider } from '@/globalComponents/ToastProvider';
import { ProtectedRoute } from '@/globalComponents/ProtectedRoute';
import { PublicOnlyRoute } from '@/globalComponents/PublicOnlyRoute';
import LoginPage from '@/pages/LoginPage/LoginPage';
import RegisterPage from '@/pages/RegisterPage/RegisterPage';
import PaymentSuccessPage from '@/pages/PaymentSuccessPage/PaymentSuccessPage';
import DashboardPage from '@/pages/DashboardPage/DashboardPage';
import BranchesPage from '@/pages/BranchesPage/BranchesPage';
import EmployeesPage from '@/pages/EmployeesPage/EmployeesPage';
import RolesPage from '@/pages/RolesPage/RolesPage';
import IngredientsPage from '@/pages/IngredientsPage/IngredientsPage';
import ProductsPage from '@/pages/ProductsPage/ProductsPage';

export function App() {
  return (
    <ToastProvider>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            {/* Public-Only Auth & Onboarding Routes (redirects to /dashboard if already logged in) */}
            <Route element={<PublicOnlyRoute />}>
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/payment-success" element={<PaymentSuccessPage />} />
            </Route>

            {/* Protected Application Routes */}
            <Route element={<ProtectedRoute />}>
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/branches" element={<BranchesPage />} />
              <Route path="/employees" element={<EmployeesPage />} />
              <Route path="/roles" element={<RolesPage />} />
              <Route path="/ingredients" element={<IngredientsPage />} />
              <Route path="/products" element={<ProductsPage />} />
            </Route>

            {/* Default Catch-all Fallback */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ToastProvider>
  );
}

export default App;
