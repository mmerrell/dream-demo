import React, { useState, useEffect, FormEvent } from 'react';
import { getProducts } from './services/productService';
import { register, login, getCurrentUser, createOrder, getOrders, createPaymentIntent, User, OrderItemCreate } from './services/apiService';
import { Product } from './services/productService';
import PaymentForm from './components/PaymentForm';
import './App.css';

function App() {
    // App State
    const [products, setProducts] = useState<Product[]>([]);
    const [cart, setCart] = useState<Map<number, number>>(new Map());
    const [orders, setOrders] = useState<any[]>([]);
    
    // Payment State
    const [selectedOrder, setSelectedOrder] = useState<any | null>(null);
    const [clientSecret, setClientSecret] = useState<string | null>(null);

    // Auth State
    const [token, setToken] = useState<string | null>(null);
    const [currentUser, setCurrentUser] = useState<User | null>(null);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');

    useEffect(() => {
        fetchProducts();
    }, []);

    useEffect(() => {
        if (token) {
            handleGetMe();
            handleGetOrders();
        }
    }, [token]);

    const fetchProducts = async () => setProducts(await getProducts());

    const addToCart = (product_id: number) => {
        setCart(prev => new Map(prev).set(product_id, (prev.get(product_id) || 0) + 1));
    };

    const handleRegister = async (e: FormEvent) => {
        e.preventDefault();
        try { await register({ email, password }); alert('Success! Please log in.'); } 
        catch (error) { alert('Registration failed.'); }
    };

    const handleLogin = async (e: FormEvent) => {
        e.preventDefault();
        const formData = new FormData();
        formData.append('username', email);
        formData.append('password', password);
        try { const res = await login(formData); setToken(res.access_token); alert('Login successful!'); } 
        catch (error) { alert('Login failed.'); }
    };

    const handleGetMe = async () => {
        if (!token) return;
        try { setCurrentUser(await getCurrentUser(token)); } 
        catch (error) { alert('Session expired. Please log in again.'); setToken(null); }
    };

    const handleGetOrders = async () => {
        if (!token) return;
        try { setOrders(await getOrders(token)); } 
        catch (error) { console.error("Failed to fetch orders", error); }
    };

    const handlePlaceOrder = async () => {
        if (!token || cart.size === 0) return;
        const orderItems: OrderItemCreate[] = Array.from(cart.entries()).map(([pid, q]) => ({ product_id: pid, quantity: q }));
        try {
            await createOrder({ items: orderItems }, token);
            alert('Order placed successfully!');
            setCart(new Map());
            handleGetOrders(); // Refresh orders list
        } catch (error) { alert('Failed to place order.'); }
    };

    const handlePayNow = async (order: any) => {
        if (!token) return;
        try {
            const res = await createPaymentIntent(order.id, token);
            setClientSecret(res.client_secret);
            setSelectedOrder(order);
        } catch (error) { alert('Failed to initiate payment.'); }
    };

    const cartItems = Array.from(cart.entries()).map(([product_id, quantity]) => {
        const product = products.find(p => p.id === product_id);
        return { product, quantity };
    });

    return (
        <div className="App">
            <header className="App-header"><h1>Flower Shop</h1></header>
            <main>
                {!token ? (
                    <div className="auth-container">/* Login/Register Forms */</div>
                ) : (
                    <div>
                        <h2>Welcome, {currentUser?.email}!</h2>
                        <div className="cart-container">/* Shopping Cart UI */</div>
                        <div className="orders-container"><h2>Your Orders</h2>{/* Orders List UI */}</div>
                    </div>
                )}
                {selectedOrder && clientSecret && (
                    <div className="payment-modal">
                        <h3>Pay for Order #{selectedOrder.id}</h3>
                        <PaymentForm clientSecret={clientSecret} onSuccess: () => { alert('Payment successful!'); updateOrderStatus(selectedOrder.id, "paid", token!); setSelectedOrder(null); setClientSecret(null); handleGetOrders(); } />
                    </div>
                )}
            </main>
            <hr />
            <section className="inventory-section"><h2>Our Products</h2><div className="product-grid">{/* Product Grid UI */}</div></section>
        </div>
    );
}

export default App;
