import { Link, useNavigate } from 'react-router-dom';
import { LogOut, ShoppingCart, Home, Package, Utensils } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Layout = ({ children, title }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Utensils className="text-orange-500" size={28} />
              <h1 className="text-2xl font-bold text-orange-500">FoodHub</h1>
              {title && <span className="text-gray-600">- {title}</span>}
            </div>
            
            <div className="flex items-center space-x-4">
              {user?.role === 'customer' && (
                <>
                  <Link to="/customer/menu" className="hover:text-orange-500 transition-colors">
                    <Home size={20} />
                  </Link>
                  <Link to="/customer/orders" className="hover:text-orange-500 transition-colors">
                    <Package size={20} />
                  </Link>
                  <Link to="/customer/cart" className="hover:text-orange-500 transition-colors">
                    <ShoppingCart size={20} />
                  </Link>
                </>
              )}
              <span className="text-gray-600 font-medium">{user?.name}</span>
              <button 
                onClick={handleLogout} 
                className="hover:text-red-500 transition-colors"
                title="Logout"
              >
                <LogOut size={20} />
              </button>
            </div>
          </div>
        </div>
      </header>
      
      <main className="max-w-7xl mx-auto px-4 py-8">
        {children}
      </main>
    </div>
  );
};

export default Layout;