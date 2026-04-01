import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import PrivateRoute from './components/PrivateRoute';

import Login from './pages/Login';
import Register from './pages/Register';

import Menu from './pages/customer/Menu';
import Cart from './pages/customer/Cart';
import Orders from './pages/customer/Orders';

import WaiterDashboard from './pages/waiter/Dashboard';

import KitchenDashboard from './pages/kitchen/Dashboard';

import AdminDashboard from './pages/admin/Dashboard';
import MenuManagement from './pages/admin/MenuManagement';
import Analytics from './pages/admin/Analytics';

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Customer Routes */}
          <Route path="/customer" element={<PrivateRoute role="customer" />}>
            <Route index element={<Navigate to="/customer/menu" replace />} />
            <Route path="menu" element={<Menu />} />
            <Route path="cart" element={<Cart />} />
            <Route path="orders" element={<Orders />} />
          </Route>

          {/* Waiter Routes */}
          <Route path="/waiter" element={<PrivateRoute role="waiter" />}>
            <Route index element={<WaiterDashboard />} />
          </Route>

          {/* Kitchen Routes */}
          <Route path="/kitchen" element={<PrivateRoute role="kitchen" />}>
            <Route index element={<KitchenDashboard />} />
          </Route>

          {/* Admin Routes */}
          <Route path="/admin" element={<PrivateRoute role="admin" />}>
            <Route index element={<AdminDashboard />} />
            <Route path="menu" element={<MenuManagement />} />
            <Route path="analytics" element={<Analytics />} />
          </Route>

          {/* Default Redirect */}
          <Route path="/" element={<Navigate to="/login" replace />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;