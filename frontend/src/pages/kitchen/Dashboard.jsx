import { useState, useEffect } from 'react';
import { kitchenAPI } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import Layout from '../../components/Layout';
import { ChefHat, Clock, AlertCircle } from 'lucide-react';

const KitchenDashboard = () => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
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
      const response = await kitchenAPI.getPendingOrders();
      setOrders(response.data);
    } catch (error) {
      console.error('Error fetching orders:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateStatus = async (orderId, newStatus) => {
    try {
      await kitchenAPI.updateOrderStatus(orderId, { status: newStatus });
      await fetchOrders();
    } catch (error) {
      console.error('Error updating status:', error);
      alert('Failed to update order status');
    }
  };

  const getNextStatus = (currentStatus) => {
    const statusFlow = {
      'Placed': 'Preparing',
      'Preparing': 'Cooking',
      'Cooking': 'Ready to Serve',
    };
    return statusFlow[currentStatus];
  };

  const getStatusColor = (status) => {
    const colors = {
      'Placed': 'bg-blue-100 text-blue-600',
      'Preparing': 'bg-yellow-100 text-yellow-600',
      'Cooking': 'bg-orange-100 text-orange-600',
    };
    return colors[status] || 'bg-gray-100 text-gray-600';
  };

  if (loading) {
    return (
      <Layout title="Kitchen Dashboard">
        <div className="flex items-center justify-center h-64">
          <div className="text-xl text-gray-600">Loading orders...</div>
        </div>
      </Layout>
    );
  }

  // Group orders by status
  const placedOrders = (orders || []).filter(o => o.status === 'Placed');
  const preparingOrders = (orders || []).filter(o => o.status === 'Preparing');
  const cookingOrders = (orders || []).filter(o => o.status === 'Cooking');

  return (
    <Layout title="Kitchen Dashboard">
      <div className="mb-6">
        <h2 className="text-3xl font-bold text-gray-800 mb-2">Active Orders</h2>
        <p className="text-gray-600">Total: {(orders || []).length} orders</p>
      </div>

      {(orders || []).length === 0 ? (
        <div className="bg-white rounded-xl p-12 text-center shadow-md">
          <ChefHat className="mx-auto text-gray-400 mb-4" size={64} />
          <h3 className="text-2xl font-bold text-gray-800 mb-2">
            No pending orders
          </h3>
          <p className="text-gray-600">All orders are completed. Great job!</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Placed Orders Column */}
          <div>
            <div className="bg-blue-100 rounded-t-lg p-3 mb-4">
              <h3 className="font-bold text-blue-800 flex items-center">
                <Clock size={20} className="mr-2" />
                New Orders ({(placedOrders || []).length})
              </h3>
            </div>
            <div className="space-y-4">
              {placedOrders.map((order) => (
                <OrderCard
                  key={order.id}
                  order={order}
                  onUpdateStatus={updateStatus}
                  getNextStatus={getNextStatus}
                  getStatusColor={getStatusColor}
                />
              ))}
            </div>
          </div>

          {/* Preparing Orders Column */}
          <div>
            <div className="bg-yellow-100 rounded-t-lg p-3 mb-4">
              <h3 className="font-bold text-yellow-800 flex items-center">
                <AlertCircle size={20} className="mr-2" />
                Preparing ({(preparingOrders || []).length})
              </h3>
            </div>
            <div className="space-y-4">
              {preparingOrders.map((order) => (
                <OrderCard
                  key={order.id}
                  order={order}
                  onUpdateStatus={updateStatus}
                  getNextStatus={getNextStatus}
                  getStatusColor={getStatusColor}
                />
              ))}
            </div>
          </div>

          {/* Cooking Orders Column */}
          <div>
            <div className="bg-orange-100 rounded-t-lg p-3 mb-4">
              <h3 className="font-bold text-orange-800 flex items-center">
                <ChefHat size={20} className="mr-2" />
                Cooking ({(cookingOrders || []).length})
              </h3>
            </div>
            <div className="space-y-4">
              {cookingOrders.map((order) => (
                <OrderCard
                  key={order.id}
                  order={order}
                  onUpdateStatus={updateStatus}
                  getNextStatus={getNextStatus}
                  getStatusColor={getStatusColor}
                />
              ))}
            </div>
          </div>
        </div>
      )}
    </Layout>
  );
};

const OrderCard = ({ order, onUpdateStatus, getNextStatus, getStatusColor }) => {
  const nextStatus = getNextStatus(order.status);

  return (
    <div className="bg-white rounded-xl shadow-md p-4 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-3">
        <div>
          <h4 className="font-bold text-gray-800">Order #{order.id}</h4>
          <p className="text-xs text-gray-500">
            {new Date(order.created_at).toLocaleTimeString()}
          </p>
          {order.table_number && (
            <p className="text-sm text-orange-500 font-semibold">
              Table: {order.table_number}
            </p>
          )}
        </div>
        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(order.status)}`}>
          {order.status}
        </span>
      </div>

      <div className="mb-3">
        <h5 className="text-sm font-semibold text-gray-700 mb-1">Items:</h5>
        <ul className="space-y-1">
          {(order?.items || []).map((item) => (
            <li key={item.id} className="text-sm text-gray-700 bg-gray-50 p-1 px-2 rounded">
              {item.item_name} <span className="font-semibold">x{item.quantity}</span>
            </li>
          ))}
        </ul>
      </div>

      {order.notes && (
        <div className="mb-3 bg-yellow-50 p-2 rounded">
          <p className="text-xs text-gray-600">
            <span className="font-semibold">Note:</span> {order.notes}
          </p>
        </div>
      )}

      <button
        onClick={() => onUpdateStatus(order.id, nextStatus)}
        className="w-full bg-orange-500 text-white py-2 rounded-lg hover:bg-orange-600 transition-colors font-semibold text-sm"
      >
        Mark as {nextStatus}
      </button>
    </div>
  );
};

export default KitchenDashboard;