import axios from 'axios';

// TODO: Move these to a central types.ts file
export interface User {
    email: string;
    id: number;
    is_active: boolean;
}
export interface UserCreate {
    email: string;
    password: string;
}
export interface OrderItemCreate {
    product_id: number;
    quantity: number;
}
export interface OrderCreate {
    items: OrderItemCreate[];
}

const API_URL = 'http://localhost:8000';

export const register = async (user: UserCreate): Promise<User> => {
    const response = await axios.post(`${API_URL}/users/`, user);
    return response.data;
};

export const login = async (formData: FormData): Promise<{ access_token: string }> => {
    const response = await axios.post(`${API_URL}/token`, formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
    return response.data;
};

export const getCurrentUser = async (token: string): Promise<User> => {
    const response = await axios.get(`${API_URL}/users/me/`, {
        headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
};

export const createOrder = async (order: OrderCreate, token: string): Promise<any> => {
    const response = await axios.post(`${API_URL}/orders/`, order, {
        headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
};

export const getOrders = async (token: string): Promise<any[]> => {
    const response = await axios.get(`${API_URL}/orders/`, {
        headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
};

export const createPaymentIntent = async (order_id: number, token: string): Promise<{ client_secret: string }> => {
    const response = await axios.post(`${API_URL}/create-payment-intent`, { order_id }, {
        headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
};

export const updateOrderStatus = async (order_id: number, status: string, token: string): Promise<any> => {
    const response = await axios.post(`${API_URL}/orders/${order_id}/update-status`, { status }, {
        headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
};
