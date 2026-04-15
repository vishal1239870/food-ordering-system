import { useState, useEffect } from 'react';
import { orderAPI } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import Layout from '../../components/Layout';
import { Clock, Package, CheckCircle } from 'lucide-react';

const Orders = () => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const { ws } = useAuth();

  useEffect(() => {
    fetchOrders();

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
      const response = await orderAPI.getMyOrders();
      setOrders(response.data);
    } catch (error) {
      console.error('Error fetching orders:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      'Placed': 'bg-blue-100 text-blue-600',
      'Preparing': 'bg-yellow-100 text-yellow-600',
      'Cooking': 'bg-orange-100 text-orange-600',
      'Ready to Serve': 'bg-purple-100 text-purple-600',
      'Served': 'bg-green-100 text-green-600',
    };
    return colors[status] || 'bg-gray-100 text-gray-600';
  };

  const getStatusIcon = (status) => {
    if (status === 'Served') return <CheckCircle size={20} />;
    if (status === 'Ready to Serve') return <Package size={20} />;
    return <Clock size={20} />;
  };

  if (loading) {
    return (
      <Layout title="My Orders">
        <div className="flex items-center justify-center h-64">
          <div className="text-xl text-gray-600">Loading orders...</div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="My Orders">
      {(orders || []).length === 0 ? (
        <div className="bg-white rounded-xl p-12 text-center shadow-md">
          <Package className="mx-auto text-gray-400 mb-4" size={64} />
          <h3 className="text-2xl font-bold text-gray-800 mb-2">No orders yet</h3>
          <p className="text-gray-600 mb-6">Start ordering some delicious food!</p>
        </div>
      ) : (
        <div>
          <h2 className="text-3xl font-bold text-gray-800 mb-6">
            My Orders ({(orders || []).length})
          </h2>
          <div className="space-y-4">
            {(orders || []).map((order) => (
              <div
                key={order.id}
                className="bg-white rounded-xl shadow-md overflow-hidden hover:shadow-lg transition-shadow"
              >
                <div className="p-6">
                  {/* Order Header */}
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="text-xl font-bold text-gray-800">
                        Order #{order.id}
                      </h3>
                      <p className="text-gray-500 text-sm">
                        {new Date(order.created_at).toLocaleString()}
                      </p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className={`px-4 py-2 rounded-full font-semibold flex items-center ${getStatusColor(order.status)}`}>
                        {getStatusIcon(order.status)}
                        <span className="ml-2">{order.status}</span>
                      </span>
                    </div>
                  </div>

                  {/* Order Items */}
                  <div className="mb-4">
                    <h4 className="font-semibold text-gray-700 mb-2">Items:</h4>
                    <div className="space-y-2">
                      {(order.items || []).map((item) => (
                        <div
                          key={item.id}
                          className="flex justify-between text-gray-700 bg-gray-50 p-2 rounded"
                        >
                          <span>
                            {item.item_name} x{item.quantity}
                          </span>
                          <span className="font-semibold">
                            ${(parseFloat(item.price) * item.quantity).toFixed(2)}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Order Notes */}
                  {order.notes && (
                    <div className="mb-4 bg-yellow-50 p-3 rounded">
                      <p className="text-sm text-gray-600">
                        <span className="font-semibold">Note:</span> {order.notes}
                      </p>
                    </div>
                  )}

                  {/* Order Footer */}
                  <div className="pt-4 border-t flex justify-between items-center">
                    <div className="text-sm text-gray-600">
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        order.payment_status === 'completed'
                          ? 'bg-green-100 text-green-600'
                          : 'bg-yellow-100 text-yellow-600'
                      }`}>
                        Payment: {order.payment_status}
                      </span>
                      {order.table_number && (
                        <span className="ml-2">Table: {order.table_number}</span>
                      )}
                    </div>
                    <div className="text-right">
                      <span className="text-sm text-gray-600">Total:</span>
                      <span className="text-2xl font-bold text-orange-500 ml-2">
                        ${parseFloat(order.total_price).toFixed(2)}
                      </span>
                    </div>
                  </div>

                  {/* Order Progress */}
                  <div className="mt-4">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-xs text-gray-500">Order Progress</span>
                      <span className="text-xs text-gray-500">
                        {order.status === 'Served' ? '100%' : 
                         order.status === 'Ready to Serve' ? '80%' :
                         order.status === 'Cooking' ? '60%' :
                         order.status === 'Preparing' ? '40%' : '20%'}
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full transition-all duration-500 ${
                          order.status === 'Served' ? 'bg-green-500 w-full' :
                          order.status === 'Ready to Serve' ? 'bg-purple-500 w-4/5' :
                          order.status === 'Cooking' ? 'bg-orange-500 w-3/5' :
                          order.status === 'Preparing' ? 'bg-yellow-500 w-2/5' :
                          'bg-blue-500 w-1/5'
                        }`}
                      />
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </Layout>
  );
};

export default Orders;