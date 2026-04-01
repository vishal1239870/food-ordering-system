import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { cartAPI, orderAPI } from '../../services/api';
import Layout from '../../components/Layout';
import { Plus, Minus, Trash2, ShoppingCart, AlertCircle } from 'lucide-react';

const Cart = () => {
  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchCart();
  }, []);

  const fetchCart = async () => {
    try {
      const response = await cartAPI.getCart();
      setCart(response.data);
    } catch (error) {
      console.error('Error fetching cart:', error);
      setError('Failed to load cart');
    } finally {
      setLoading(false);
    }
  };

  const updateQuantity = async (itemId, newQuantity) => {
    if (newQuantity < 1) {
      await removeItem(itemId);
      return;
    }

    try {
      await cartAPI.updateCartItem(itemId, { quantity: newQuantity });
      await fetchCart();
    } catch (error) {
      console.error('Error updating quantity:', error);
      setError('Failed to update quantity');
    }
  };

  const removeItem = async (itemId) => {
    try {
      await cartAPI.removeFromCart(itemId);
      await fetchCart();
    } catch (error) {
      console.error('Error removing item:', error);
      setError('Failed to remove item');
    }
  };

  const clearCart = async () => {
    if (!window.confirm('Are you sure you want to clear your cart?')) return;
    
    try {
      await cartAPI.clearCart();
      await fetchCart();
    } catch (error) {
      console.error('Error clearing cart:', error);
      setError('Failed to clear cart');
    }
  };

  const placeOrder = async () => {
    if (!cart || cart.items.length === 0) return;

    setProcessing(true);
    try {
      const response = await orderAPI.createOrder({});
      const orderId = response.data.id;
      
      // Process payment
      await orderAPI.processPayment(orderId, { payment_method: 'card' });
      
      alert('Order placed successfully!');
      navigate('/customer/orders');
    } catch (error) {
      console.error('Error placing order:', error);
      setError(error.response?.data?.detail || 'Failed to place order');
    } finally {
      setProcessing(false);
    }
  };

  if (loading) {
    return (
      <Layout title="Shopping Cart">
        <div className="flex items-center justify-center h-64">
          <div className="text-xl text-gray-600">Loading cart...</div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Shopping Cart">
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4 flex items-center">
          <AlertCircle size={20} className="mr-2" />
          <span>{error}</span>
        </div>
      )}

      {!cart || cart.items.length === 0 ? (
        <div className="bg-white rounded-xl p-12 text-center shadow-md">
          <ShoppingCart className="mx-auto text-gray-400 mb-4" size={64} />
          <h3 className="text-2xl font-bold text-gray-800 mb-2">Your cart is empty</h3>
          <p className="text-gray-600 mb-6">Add some delicious items from our menu!</p>
          <button
            onClick={() => navigate('/customer/menu')}
            className="bg-orange-500 text-white px-6 py-3 rounded-lg hover:bg-orange-600 transition-colors font-semibold"
          >
            Browse Menu
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Cart Items */}
          <div className="lg:col-span-2 space-y-4">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-bold text-gray-800">
                Cart Items ({cart.items.length})
              </h2>
              <button
                onClick={clearCart}
                className="text-red-500 hover:text-red-600 transition-colors flex items-center"
              >
                <Trash2 size={18} className="mr-1" />
                Clear Cart
              </button>
            </div>

            {cart.items.map((item) => (
              <div
                key={item.id}
                className="bg-white rounded-xl shadow-md p-6 flex items-center justify-between"
              >
                <div className="flex-1">
                  <h3 className="font-bold text-gray-800 text-lg">{item.item_name}</h3>
                  <p className="text-gray-600 text-sm mb-2">{item.item_description}</p>
                  <p className="text-orange-500 font-semibold">
                    ${parseFloat(item.price).toFixed(2)} each
                  </p>
                </div>

                <div className="flex items-center space-x-4 ml-4">
                  <div className="flex items-center space-x-2 bg-gray-100 rounded-lg p-1">
                    <button
                      onClick={() => updateQuantity(item.item_id, item.quantity - 1)}
                      className="bg-white p-2 rounded hover:bg-gray-200 transition-colors"
                    >
                      <Minus size={16} />
                    </button>
                    <span className="font-semibold w-8 text-center">{item.quantity}</span>
                    <button
                      onClick={() => updateQuantity(item.item_id, item.quantity + 1)}
                      className="bg-white p-2 rounded hover:bg-gray-200 transition-colors"
                    >
                      <Plus size={16} />
                    </button>
                  </div>

                  <div className="text-right min-w-[80px]">
                    <p className="font-bold text-gray-800 text-lg">
                      ${(parseFloat(item.price) * item.quantity).toFixed(2)}
                    </p>
                  </div>

                  <button
                    onClick={() => removeItem(item.item_id)}
                    className="text-red-500 hover:text-red-600 transition-colors p-2"
                    title="Remove item"
                  >
                    <Trash2 size={20} />
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Order Summary */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-md p-6 sticky top-24">
              <h3 className="text-xl font-bold text-gray-800 mb-4">Order Summary</h3>
              
              <div className="space-y-3 mb-6">
                <div className="flex justify-between text-gray-600">
                  <span>Subtotal:</span>
                  <span>${parseFloat(cart.total).toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-gray-600">
                  <span>Tax (10%):</span>
                  <span>${(parseFloat(cart.total) * 0.1).toFixed(2)}</span>
                </div>
                
                <div className="border-t pt-3 mt-3">
                  <div className="flex justify-between items-center">
                    <span className="text-xl font-bold text-gray-800">Total:</span>
                    <span className="text-2xl font-bold text-orange-500">
                      ${(parseFloat(cart.total) * 1.1 ).toFixed(2)}
                    </span>
                  </div>
                </div>
              </div>

              <button
                onClick={placeOrder}
                disabled={processing}
                className="w-full bg-orange-500 text-white py-3 rounded-lg hover:bg-orange-600 transition-colors font-semibold text-lg disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {processing ? 'Processing...' : 'Place Order & Pay'}
              </button>

              <p className="text-gray-500 text-xs text-center mt-4">
                By placing order, you agree to our terms and conditions
              </p>
            </div>
          </div>
        </div>
      )}
    </Layout>
  );
};

export default Cart;