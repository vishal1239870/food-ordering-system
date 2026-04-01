import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { adminAPI } from '../../services/api';
import Layout from '../../components/Layout';
import { TrendingUp, DollarSign, ShoppingBag, Users, ChefHat, Settings } from 'lucide-react';

const AdminDashboard = () => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const response = await adminAPI.getAnalytics();
      setAnalytics(response.data);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Layout title="Admin Dashboard">
        <div className="flex items-center justify-center h-64">
          <div className="text-xl text-gray-600">Loading analytics...</div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Admin Dashboard">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-800 mb-2">Dashboard Overview</h2>
        <p className="text-gray-600">Welcome back! Here's what's happening today.</p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Today's Revenue"
          value={`$${analytics.today.revenue.toFixed(2)}`}
          icon={<DollarSign size={24} />}
          color="bg-green-500"
        />
        <StatCard
          title="Today's Orders"
          value={analytics.today.orders}
          icon={<ShoppingBag size={24} />}
          color="bg-blue-500"
        />
        <StatCard
          title="Active Orders"
          value={analytics.today.active_orders}
          icon={<ChefHat size={24} />}
          color="bg-orange-500"
        />
        <StatCard
          title="Weekly Revenue"
          value={`$${analytics.week.revenue.toFixed(2)}`}
          icon={<TrendingUp size={24} />}
          color="bg-purple-500"
        />
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8 ">
        <Link
          to="/admin/menu"
          className="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition-shadow text-center"
        >
          <ChefHat className="mx-auto text-orange-500 mb-3" size={48} />
          <h3 className="text-xl font-bold text-gray-800 mb-2">Menu Management</h3>
          <p className="text-gray-600 text-sm">Add, edit, or remove menu items</p>
        </Link>

        <Link
          to="/admin/analytics"
          className="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition-shadow text-center"
        >
          <TrendingUp className="mx-auto text-blue-500 mb-3" size={48} />
          <h3 className="text-xl font-bold text-gray-800 mb-2">Analytics</h3>
          <p className="text-gray-600 text-sm">View detailed reports and insights</p>
        </Link>

        
      </div>

      {/* Analytics Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Order Status Breakdown */}
        <div className="bg-white rounded-xl shadow-md p-6">
          <h3 className="text-xl font-bold text-gray-800 mb-4">Order Status Breakdown</h3>
          <div className="space-y-3">
            {Object.entries(analytics.status_breakdown).map(([status, count]) => (
              <div key={status} className="flex justify-between items-center">
                <span className="text-gray-700">{status}</span>
                <span className="bg-gray-100 px-3 py-1 rounded-full font-semibold">
                  {count}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Popular Items */}
        <div className="bg-white rounded-xl shadow-md p-6">
          <h3 className="text-xl font-bold text-gray-800 mb-4">Popular Items</h3>
          <div className="space-y-3">
            {analytics.popular_items.slice(0, 5).map((item, index) => (
              <div key={index} className="flex justify-between items-center">
                <span className="text-gray-700">{item.name}</span>
                <span className="bg-orange-100 text-orange-600 px-3 py-1 rounded-full font-semibold text-sm">
                  {item.quantity} sold
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Monthly Stats */}
      <div className="mt-6 bg-white rounded-xl shadow-md p-6">
        <h3 className="text-xl font-bold text-gray-800 mb-4">Monthly Performance</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <p className="text-gray-600 mb-2">Total Orders</p>
            <p className="text-3xl font-bold text-gray-800">{analytics.month.orders}</p>
          </div>
          <div>
            <p className="text-gray-600 mb-2">Total Revenue</p>
            <p className="text-3xl font-bold text-green-600">
              ${analytics.month.revenue.toFixed(2)}
            </p>
          </div>
        </div>
      </div>
    </Layout>
  );
};

const StatCard = ({ title, value, icon, color }) => (
  <div className="bg-white rounded-xl shadow-md p-6">
    <div className="flex items-center justify-between mb-4">
      <div className={`${color} p-3 rounded-lg text-white`}>{icon}</div>
    </div>
    <p className="text-gray-600 text-sm mb-1">{title}</p>
    <p className="text-3xl font-bold text-gray-800">{value}</p>
  </div>
);

export default AdminDashboard;