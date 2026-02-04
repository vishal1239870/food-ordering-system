import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Utensils, AlertCircle } from 'lucide-react';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const user = await login(email, password);
      navigate(`/${user.role}`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const quickLogin = (role) => {
    const credentials = {
      admin: { email: 'admin@foodhub.com', password: 'admin123' },
      customer: { email: 'john@example.com', password: 'admin123' },
      waiter: { email: 'jane@foodhub.com', password: 'admin123' },
      kitchen: { email: 'mike@foodhub.com', password: 'admin123' },
    };
    
    setEmail(credentials[role].email);
    setPassword(credentials[role].password);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-orange-400 to-red-500 p-4">
      <div className="bg-white p-8 rounded-2xl shadow-2xl w-full max-w-md">
        <div className="text-center mb-6">
          <div className="bg-orange-500 w-16 h-16 rounded-full mx-auto mb-4 flex items-center justify-center">
            <Utensils className="text-white" size={32} />
          </div>
          <h1 className="text-3xl font-bold text-gray-800">FoodHub</h1>
          <p className="text-gray-600 mt-2">Sign in to your account</p>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4 flex items-center">
            <AlertCircle size={20} className="mr-2" />
            <span className="text-sm">{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email Address
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none transition"
              placeholder="Enter your email"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none transition"
              placeholder="Enter your password"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-orange-500 text-white py-3 rounded-lg hover:bg-orange-600 transition-colors font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div className="mt-4 text-center">
          <p className="text-gray-600 text-sm">
            Don't have an account?{' '}
            <Link to="/register" className="text-orange-500 hover:underline font-semibold">
              Register here
            </Link>
          </p>
        </div>

        <div className="mt-6 p-4 bg-gray-100 rounded-lg">
          <p className="text-sm text-gray-600 font-semibold mb-3">Quick Login (Demo):</p>
          <div className="grid grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() => quickLogin('customer')}
              className="bg-blue-500 text-white px-3 py-2 rounded text-xs hover:bg-blue-600 transition"
            >
              Customer
            </button>
            <button
              type="button"
              onClick={() => quickLogin('waiter')}
              className="bg-green-500 text-white px-3 py-2 rounded text-xs hover:bg-green-600 transition"
            >
              Waiter
            </button>
            <button
              type="button"
              onClick={() => quickLogin('kitchen')}
              className="bg-purple-500 text-white px-3 py-2 rounded text-xs hover:bg-purple-600 transition"
            >
              Kitchen
            </button>
            <button
              type="button"
              onClick={() => quickLogin('admin')}
              className="bg-red-500 text-white px-3 py-2 rounded text-xs hover:bg-red-600 transition"
            >
              Admin
            </button>
          </div>
          
        </div>
      </div>
    </div>
  );
};

export default Login;