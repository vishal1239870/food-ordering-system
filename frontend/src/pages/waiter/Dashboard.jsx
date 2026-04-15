import { useState, useEffect } from 'react';
import { waiterAPI } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import Layout from '../../components/Layout';
import { CheckCircle, Clock, AlertCircle } from 'lucide-react';

const WaiterDashboard = () => {
  const [readyOrders, setReadyOrders] = useState([]);
  const [allOrders, setAllOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('ready');
  const { ws } = useAuth();

  useEffect(() => {
    fetchOrders();

    // Subscribe to WebSocket updates
    if (ws) {
      const handleOrderUpdate = (data) => {
        if (data.type === 'order_update') {
          fetchOrders();
        }
      };
      ws.subscribe(handleOrderUpdate);

      return () => {
        ws.unsubscribe(handleOrderUpdate);
      };
    }
  }, [ws]);

  const fetchOrders = async () => {
    try {
      const [readyResponse, allResponse] = await Promise.all([
        waiterAPI.getReadyOrders(),
        waiterAPI.getAllActiveOrders(),
      ]);
      setReadyOrders(readyResponse.data);
      setAllOrders(allResponse.data);
    } catch (error) {
      console.error('Error fetching orders:', error);
    } finally {
      setLoading(false);
    }
  };

  const markAsServed = async (orderId) => {
    if (!window.confirm('Mark this order as served?')) return;

    try {
      await waiterAPI.markServed(orderId);
      await fetchOrders();
    } catch (error) {
      console.error('Error marking order as served:', error);
      alert('Failed to mark order as served');
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      'Placed': 'bg-blue-100 text-blue-600',
      'Preparing': 'bg-yellow-100 text-yellow-600',
      'Cooking': 'bg-orange-100 text-orange-600',
      'Ready to Serve': 'bg-purple-100 text-purple-600',
    };
    return colors[status] || 'bg-gray-100 text-gray-600';
  };

  const OrderCard = ({ order, showServeButton }) => (
    <div className="bg-white rounded-xl shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-xl font-bold text-gray-800">Order #{order.id}</h3>
          <p className="text-gray-600 text-sm">
            {new Date(order.created_at).toLocaleString()}
          </p>
          {order.table_number && (
            <p className="text-orange-500 font-semibold mt-1">
              Table: {order.table_number}
            </p>
          )}
        </div>
        <span className={`px-4 py-2 rounded-full font-semibold ${getStatusColor(order.status)}`}>
          {order.status}
        </span>
      </div>

      <div className="mb-4">
        <h4 className="font-semibold text-gray-700 mb-2">Items:</h4>
        <ul className="space-y-1">
          {(order.items || []).map((item) => (
            <li key={item.id} className="text-gray-700 bg-gray-50 p-2 rounded">
              • {item.item_name} x{item.quantity}
            </li>
          ))}
        </ul>
      </div>

      {order.notes && (
        <div className="mb-4 bg-yellow-50 p-3 rounded">
          <p className="text-sm text-gray-600">
            <span className="font-semibold">Note:</span> {order.notes}
          </p>
        </div>
      )}

      <div className="pt-4 border-t">
        <div className="flex justify-between items-center mb-4">
          <span className="font-semibold text-gray-700">Total:</span>
          <span className="text-xl font-bold text-orange-500">
            ${parseFloat(order.total_price).toFixed(2)}
          </span>
        </div>

        {showServeButton && (
          <button
            onClick={() => markAsServed(order.id)}
            className="w-full bg-green-500 text-white py-3 rounded-lg hover:bg-green-600 transition-colors font-semibold flex items-center justify-center"
          >
            <CheckCircle size={20} className="mr-2" />
            Mark as Served
          </button>
        )}
      </div>
    </div>
  );

  if (loading) {
    return (
      <Layout title="Waiter Dashboard">
        <div className="flex items-center justify-center h-64">
          <div className="text-xl text-gray-600">Loading orders...</div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Waiter Dashboard">
      {/* Tabs */}
      <div className="flex space-x-4 mb-6">
        <button
          onClick={() => setActiveTab('ready')}
          className={`px-6 py-3 rounded-lg font-semibold transition-colors ${
            activeTab === 'ready'
              ? 'bg-orange-500 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          Ready to Serve ({(readyOrders || []).length})
        </button>
        <button
          onClick={() => setActiveTab('all')}
          className={`px-6 py-3 rounded-lg font-semibold transition-colors ${
            activeTab === 'all'
              ? 'bg-orange-500 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          All Active ({(allOrders || []).length})
        </button>
      </div>

      {/* Ready to Serve Tab */}
      {activeTab === 'ready' && (
        <div>
          <h2 className="text-3xl font-bold text-gray-800 mb-6">
            Ready to Serve
          </h2>
          {(readyOrders || []).length === 0 ? (
            <div className="bg-white rounded-xl p-12 text-center shadow-md">
              <CheckCircle className="mx-auto text-green-500 mb-4" size={64} />
              <h3 className="text-2xl font-bold text-gray-800 mb-2">
                All orders served!
              </h3>
              <p className="text-gray-600">No orders waiting to be served right now.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {(readyOrders || []).map((order) => (
                <OrderCard key={order.id} order={order} showServeButton={true} />
              ))}
            </div>
          )}
        </div>
      )}

      {/* All Active Orders Tab */}
      {activeTab === 'all' && (
        <div>
          <h2 className="text-3xl font-bold text-gray-800 mb-6">
            All Active Orders
          </h2>
          {(allOrders || []).length === 0 ? (
            <div className="bg-white rounded-xl p-12 text-center shadow-md">
              <Clock className="mx-auto text-gray-400 mb-4" size={64} />
              <h3 className="text-2xl font-bold text-gray-800 mb-2">
                No active orders
              </h3>
              <p className="text-gray-600">All orders have been completed.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {(allOrders || []).map((order) => (
                <OrderCard 
                  key={order.id} 
                  order={order} 
                  showServeButton={order.status === 'Ready to Serve'} 
                />
              ))}
            </div>
          )}
        </div>
      )}
    </Layout>
  );
};

export default WaiterDashboard;