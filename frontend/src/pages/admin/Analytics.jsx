import { useState, useEffect } from 'react';
import { adminAPI } from '../../services/api';
import Layout from '../../components/Layout';
import { TrendingUp, DollarSign } from 'lucide-react';

const Analytics = () => {
  const [analytics, setAnalytics] = useState(null);
  const [orderAnalytics, setOrderAnalytics] = useState(null);
  const [days, setDays] = useState(7);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, [days]);

  const fetchData = async () => {
    try {
      const [analyticsRes, ordersRes] = await Promise.all([
        adminAPI.getAnalytics(),
        adminAPI.getOrdersAnalytics(days),
      ]);
      setAnalytics(analyticsRes.data);
      setOrderAnalytics(ordersRes.data);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Layout title="Analytics">
        <div className="flex items-center justify-center h-64">
          <div className="text-xl text-gray-600">Loading analytics...</div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Analytics">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-800 mb-2">Analytics & Reports</h2>
        <p className="text-gray-600">Detailed insights into your restaurant performance</p>
      </div>

      {/* Period Selector */}
      <div className="mb-6 flex space-x-2">
        {[7, 14, 30].map((period) => (
          <button
            key={period}
            onClick={() => setDays(period)}
            className={`px-4 py-2 rounded-lg font-semibold transition-colors ${
              days === period
                ? 'bg-orange-500 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Last {period} days
          </button>
        ))}
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-xl shadow-md p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-gray-600 font-semibold">Total Revenue</h3>
            <DollarSign className="text-green-500" size={24} />
          </div>
          <p className="text-3xl font-bold text-gray-800">
            ${orderAnalytics.daily_stats.reduce((sum, day) => sum + day.revenue, 0).toFixed(2)}
          </p>
          <p className="text-sm text-gray-500 mt-2">Last {days} days</p>
        </div>

        <div className="bg-white rounded-xl shadow-md p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-gray-600 font-semibold">Total Orders</h3>
            <TrendingUp className="text-blue-500" size={24} />
          </div>
          <p className="text-3xl font-bold text-gray-800">
            {orderAnalytics.daily_stats.reduce((sum, day) => sum + day.orders, 0)}
          </p>
          <p className="text-sm text-gray-500 mt-2">Last {days} days</p>
        </div>

        <div className="bg-white rounded-xl shadow-md p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-gray-600 font-semibold">Average Order</h3>
            <DollarSign className="text-purple-500" size={24} />
          </div>
          <p className="text-3xl font-bold text-gray-800">
            ${(
              orderAnalytics.daily_stats.reduce((sum, day) => sum + day.revenue, 0) /
              orderAnalytics.daily_stats.reduce((sum, day) => sum + day.orders, 0)
            ).toFixed(2)}
          </p>
          <p className="text-sm text-gray-500 mt-2">Per order</p>
        </div>
      </div>

      {/* Daily Stats Table */}
      <div className="bg-white rounded-xl shadow-md overflow-hidden mb-8">
        <div className="p-6 border-b">
          <h3 className="text-xl font-bold text-gray-800">Daily Breakdown</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Orders
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Revenue
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Avg Order
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {orderAnalytics.daily_stats.map((day) => (
                <tr key={day.date} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-gray-800">
                    {new Date(day.date).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 font-semibold text-gray-800">
                    {day.orders}
                  </td>
                  <td className="px-6 py-4 font-semibold text-green-600">
                    ${day.revenue.toFixed(2)}
                  </td>
                  <td className="px-6 py-4 text-gray-800">
                    ${(day.revenue / day.orders).toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Popular Items */}
      <div className="bg-white rounded-xl shadow-md p-6">
        <h3 className="text-xl font-bold text-gray-800 mb-4">Top Selling Items</h3>
        <div className="space-y-3">
          {analytics.popular_items.map((item, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center">
                <span className="bg-orange-500 text-white w-8 h-8 rounded-full flex items-center justify-center font-bold mr-3">
                  {index + 1}
                </span>
                <span className="font-semibold text-gray-800">{item.name}</span>
              </div>
              <span className="bg-orange-100 text-orange-600 px-4 py-1 rounded-full font-semibold">
                {item.quantity} sold
              </span>
            </div>
          ))}
        </div>
      </div>
    </Layout>
  );
};

export default Analytics;