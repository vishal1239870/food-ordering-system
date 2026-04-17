import { useState, useEffect } from 'react';
import { menuAPI, cartAPI } from '../../services/api';
import Layout from '../../components/Layout';
import { ShoppingCart, AlertCircle, CheckCircle } from 'lucide-react';

const Menu = () => {
  const [menuItems, setMenuItems] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState({ type: '', text: '' });

  useEffect(() => {
    fetchMenu();
    fetchCategories();
  }, []);

  const fetchMenu = async () => {
    try {
      const response = await menuAPI.getMenu();
      setMenuItems(response.data);
    } catch (error) {
      console.error('Error fetching menu:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await menuAPI.getCategories();
      setCategories(['all', ...response.data.categories]);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const addToCart = async (item) => {
    try {
      await cartAPI.addToCart({ item_id: item.id, quantity: 1 });
      setMessage({ type: 'success', text: `${item.name} added to cart!` });
      setTimeout(() => setMessage({ type: '', text: '' }), 3000);
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to add to cart' });
      setTimeout(() => setMessage({ type: '', text: '' }), 3000);
    }
  };

  const filteredItems =
    selectedCategory === 'all'
      ? menuItems
      : (menuItems || []).filter((item) => {
          if (!item.category) return false;
          const itemCat = item.category.toLowerCase().trim();
          const selectedCat = selectedCategory.toLowerCase().trim();
          // Check for exact match or if one string contains the other (to handle Burger vs Burgers)
          return itemCat === selectedCat || itemCat.includes(selectedCat) || selectedCat.includes(itemCat);
        });

  if (loading) {
    return (
      <Layout title="Menu">
        <div className="flex items-center justify-center h-64">
          <div className="text-xl text-gray-600">Loading menu...</div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Menu">
      {message.text && (
        <div
          className={`fixed top-20 right-4 z-50 px-6 py-3 rounded-lg shadow-lg flex items-center ${
            message.type === 'success' ? 'bg-green-500' : 'bg-red-500'
          } text-white`}
        >
          {message.type === 'success' ? (
            <CheckCircle size={20} className="mr-2" />
          ) : (
            <AlertCircle size={20} className="mr-2" />
          )}
          {message.text}
        </div>
      )}

      <div className="mb-6">
        <h2 className="text-3xl font-bold text-gray-800 mb-4">Our Menu</h2>
        <div className="flex flex-wrap gap-2">
          {(categories || []).map((category) => (
            <button
              key={category}
              onClick={() => setSelectedCategory(category)}
              className={`px-4 py-2 rounded-full font-medium transition-colors ${
                selectedCategory === category
                  ? 'bg-orange-500 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {category.charAt(0).toUpperCase() + category.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {(filteredItems || []).length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-600 text-lg">No items found in this category</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {(filteredItems || []).map((item) => (
            <div
              key={item.id}
              className="bg-white rounded-xl shadow-md overflow-hidden hover:shadow-xl transition-shadow"
            >
              {/* Image */}
              <div className="h-48 w-full overflow-hidden rounded-t-xl flex items-center justify-center bg-gray-100">
                <img
                  src={item.image_url || '/fallback-image.jpg'} // fallback if no image
                  alt={item.name}
                  className="h-full w-full object-cover"
                />
              </div>

              <div className="p-6">
                <div className="flex items-start justify-between mb-2">
                  <h3 className="text-xl font-bold text-gray-800 flex-1">{item.name}</h3>
                  <span className="bg-orange-100 text-orange-600 px-3 py-1 rounded-full text-sm font-semibold ml-2">
                    ${parseFloat(item.price).toFixed(2)}
                  </span>
                </div>
                <p className="text-gray-600 text-sm mb-2">{item.category}</p>
                <p className="text-gray-500 text-sm mb-4 line-clamp-2">
                  {item.description || 'Delicious food item'}
                </p>
                {item.available ? (
                  <button
                    onClick={() => addToCart(item)}
                    className="w-full bg-orange-500 text-white py-2 rounded-lg hover:bg-orange-600 transition-colors font-semibold flex items-center justify-center"
                  >
                    <ShoppingCart size={18} className="mr-2" />
                    Add to Cart
                  </button>
                ) : (
                  <button
                    disabled
                    className="w-full bg-gray-300 text-gray-500 py-2 rounded-lg cursor-not-allowed font-semibold"
                  >
                    Unavailable
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </Layout>
  );
};

export default Menu;
