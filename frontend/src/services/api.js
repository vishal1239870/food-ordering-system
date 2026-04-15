import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';


const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle authentication errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  register: (data) => api.post('/api/auth/register', data),
  login: (data) => api.post('/api/auth/login', data),
  googleLogin: (token) => api.post('/api/auth/google-login', { token }),
  getMe: () => api.get('/api/auth/me'),
  logout: () => api.post('/api/auth/logout'),
};

export const menuAPI = {
  getMenu: (params) => api.get('/api/menu', { params }),
  getMenuItem: (id) => api.get(`/api/menu/${id}`),
  getCategories: () => api.get('/api/menu/categories/list'),
};

export const cartAPI = {
  getCart: () => api.get('/api/cart'),
  addToCart: (data) => api.post('/api/cart/items', data),
  updateCartItem: (itemId, data) => api.put(`/api/cart/items/${itemId}`, data),
  removeFromCart: (itemId) => api.delete(`/api/cart/items/${itemId}`),
  clearCart: () => api.delete('/api/cart/clear'),
};

export const orderAPI = {
  createOrder: (data) => api.post('/api/orders', data),
  getMyOrders: () => api.get('/api/orders'),
  getOrder: (id) => api.get(`/api/orders/${id}`),
  processPayment: (orderId, data) => api.post(`/api/orders/${orderId}/payment`, data),
};

export const kitchenAPI = {
  getPendingOrders: () => api.get('/api/kitchen/orders'),
  updateOrderStatus: (orderId, data) => api.put(`/api/kitchen/orders/${orderId}/status`, data),
};

export const waiterAPI = {
  getReadyOrders: () => api.get('/api/waiter/orders'),
  markServed: (orderId) => api.put(`/api/waiter/orders/${orderId}/serve`),
  getAllActiveOrders: () => api.get('/api/waiter/orders/all'),
};

export const adminAPI = {
  createMenuItem: (data) => api.post('/api/admin/menu', data),
  updateMenuItem: (id, data) => api.put(`/api/admin/menu/${id}`, data),
  deleteMenuItem: (id) => api.delete(`/api/admin/menu/${id}`),
  toggleAvailability: (id) => api.put(`/api/admin/menu/${id}/toggle`),
  getAnalytics: () => api.get('/api/admin/analytics/overview'),
  getOrdersAnalytics: (days) => api.get('/api/admin/analytics/orders', { params: { days } }),
  getUsers: () => api.get('/api/admin/users'),
};

// WebSocket connection
export class OrderWebSocket {
  constructor(token) {
    this.token = token;
    this.ws = null;
    this.listeners = [];
  }

  connect() {
    let wsBase = import.meta.env.VITE_WS_URL;
    
    // Auto-detect URL for production/relative paths
    if (!wsBase || wsBase === '/' || wsBase.startsWith('/')) {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host = window.location.host;
      // If wsBase is a path other than just '/', append it
      const path = (wsBase && wsBase !== '/') ? wsBase : '';
      wsBase = `${protocol}//${host}${path}`;
    }

    // Ensure no double slashes before /ws/
    const wsURL = `${wsBase.replace(/\/$/, '')}/ws/${this.token}`;

    this.ws = new WebSocket(wsURL);

    this.ws.onopen = () => {
      console.log('WebSocket connected');
    };

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.listeners.forEach(callback => callback(data));
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
      setTimeout(() => this.connect(), 3000);
    };
  }

  subscribe(callback) {
    this.listeners.push(callback);
  }

  unsubscribe(callback) {
    this.listeners = this.listeners.filter(cb => cb !== callback);
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
    }
  }
}

export default api;