import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const login = (credentials) => api.post('/login/', credentials);
export const signup = (userData) => api.post('/signup/', userData);
export const getProfile = (userId) => api.get(`/profile/${userId}/`);
export const updateProfile = (userId, data) => api.post(`/profile/${userId}/`, data);
export const queryAI = (data) => api.post('/ai-query/', data);
export const placeOrder = (data) => api.post('/order/', data);
export const bulkPlaceOrder = (data) => api.post('/bulk-order/', data);
export const getOrders = (userId) => api.get(`/orders/${userId}/`);
export const cancelOrder = (data) => api.post('/cancel-order/', data);

// Cart API functions
export const getCart = (userId) => api.get(`/cart/?user_id=${userId}`);
export const addToCart = (data) => api.post('/cart/add/', data);
export const updateCart = (data) => api.put('/cart/update/', data);
export const removeFromCart = (data) => api.delete('/cart/remove/', { data });
export const clearCart = (data) => api.delete('/cart/clear/', { data });

// Wishlist API functions
export const getWishlist = (userId) => api.get(`/wishlist/?user_id=${userId}`);
export const addToWishlist = (data) => api.post('/wishlist/add/', data);
export const removeFromWishlist = (data) => api.delete('/wishlist/remove/', { data });
export const toggleWishlist = (data) => api.post('/wishlist/toggle/', data);

export default api;
