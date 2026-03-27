import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: `${API_BASE_URL}/api/public`,
});

export const publicApi = {
    getMenu: () => api.get('/menu/'),
    createOrder: (orderData) => api.post('/orders/', orderData),
    trackOrder: (orderNumber, phone) =>
        api.get(`/track/${orderNumber}/`, { params: { phone } }),

    // QR Ordering Endpoints
    getTableFromQR: (code) => axios.get(`${API_BASE_URL}/api/tables/from-qr/${code}/`),
    createSession: (tableId) => axios.post(`${API_BASE_URL}/api/tables/sessions/create_session/`, { table_id: tableId }),
    submitCustomerOrder: (orderData) => axios.post(`${API_BASE_URL}/api/orders/customer_order/`, orderData),

    // Loyalty Endpoints
    getActiveCampaign: () => api.get('/loyalty/campaigns/active/'),
    getCustomerInfo: (phone) => api.post('/loyalty/customer-info/', { phone }),

    // Offer & Coupon Endpoints
    getOffers: () => api.get('/offers/'),
    applyCoupon: (code, subtotal) => api.post('/apply-coupon/', { code, subtotal }),
};
