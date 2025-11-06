import React, { useState, useEffect, FormEvent } from 'react';
import { getProducts } from './services/productService';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Chip from '@mui/material/Chip';
import { Elements } from '@stripe/react-stripe-js';
import { loadStripe } from '@stripe/stripe-js';
import {
    register,
    login,
    getCurrentUser,
    createOrder,
    getOrders,
    createPaymentIntent,
    User,
    OrderItemCreate,
    updateOrderStatus
} from './services/apiService';
import { Product } from './services/productService';
import PaymentForm from './components/PaymentForm';
import './App.css';

// Add this RIGHT AFTER your imports, BEFORE the App component
const stripePromise = loadStripe(process.env.REACT_APP_STRIPE_PUBLISHABLE_KEY!);

function App() {
    // App State
    const [products, setProducts] = useState<Product[]>([]);
    const [cart, setCart] = useState<Map<number, number>>(new Map());
    const [orders, setOrders] = useState<any[]>([]);
    
    // Payment State
    const [selectedOrder, setSelectedOrder] = useState<any | null>(null);
    const [clientSecret, setClientSecret] = useState<string | null>(null);

    // Auth State
    const [token, setToken] = useState<string | null>(
        localStorage.getItem('authToken')  // <-- Updated this line
    );
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

    const removeFromCart = (product_id: number) => {
        setCart(prev => {
            const newCart = new Map(prev);
            const currentQty = newCart.get(product_id) || 0;
            if (currentQty > 1) {
                newCart.set(product_id, currentQty - 1);
            } else {
                newCart.delete(product_id);
            }
            return newCart;
        });
    };

    const handleRegister = async (e: FormEvent) => {
        e.preventDefault();
        try {
            await register({ email, password });
            alert('Success! Please log in.');
            setEmail('');
            setPassword('');
        }
        catch (error) { alert('Registration failed.'); }
    };

    const handleLogin = async (e: FormEvent) => {
        e.preventDefault();
        const formData = new FormData();
        formData.append('username', email);
        formData.append('password', password);
        try {
            const res = await login(formData);
            setToken(res.access_token);
            localStorage.setItem('authToken', res.access_token); // Add this line
            alert('Login successful!');
        }
        catch (error) { alert('Login failed.'); }
    };

    const handleGetMe = async () => {
        if (!token) return;
        try {
            setCurrentUser(await getCurrentUser(token));
        }
        catch (error) {
            alert('Session expired. Please log in again.');
            setToken(null);
            localStorage.removeItem('authToken'); // Add this line
        }
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
            handleGetOrders();
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

    const cartTotal = cartItems.reduce((sum, item) => {
        return sum + (Number(item.product?.price) || 0) * item.quantity;
    }, 0);

    const getStatusChip = (status: string) => {
        const statusConfig: Record<string, { color: any; icon?: string }> = {
            pending: { color: 'warning', icon: '⏳' },
            paid: { color: 'success', icon: '✓' },
            completed: { color: 'info', icon: '✓✓' },
            cancelled: { color: 'error', icon: '✗' }
        };

        const config = statusConfig[status] || { color: 'default', icon: '?' };

        return (
            <Chip
                label={`${config.icon} ${status.toUpperCase()}`}
                color={config.color}
                size="small"
            />
        );
    };

    return (
        <div className="App">
            <header className="App-header">
                <div className="header-left">
                    <img src="/logo.png" alt="Flower Shop Logo" className="logo" />
                    <h1>Flower Shop</h1>
                </div>
                {token && (
                    <Button
                        variant="outlined"
                        color="inherit"
                        onClick={() => {
                            setToken(null);
                            setCurrentUser(null);
                            localStorage.removeItem('authToken');
                        }}
                    >
                        Logout
                    </Button>
                )}
            </header>
            <main>
                {!token ? (
                    <div className="auth-container">
                        <div className="auth-form">
                            <h2>Register</h2>
                            <form onSubmit={handleRegister}>
                                <TextField
                                    type="email"
                                    label="Email"
                                    variant="outlined"
                                    fullWidth
                                    margin="normal"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    required
                                />
                                <TextField
                                    type="password"
                                    label="Password"
                                    variant="outlined"
                                    fullWidth
                                    margin="normal"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    required
                                />
                                <Button
                                    type="submit"
                                    variant="contained"
                                    color="primary"
                                    fullWidth
                                    sx={{ mt: 2 }}
                                >
                                    Register
                                </Button>
                            </form>
                        </div>
                        <div className="auth-form">
                            <h2>Login</h2>
                            <form onSubmit={handleLogin}>
                                <TextField
                                    type="email"
                                    label="Email"
                                    variant="outlined"
                                    fullWidth
                                    margin="normal"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    required
                                />
                                <TextField
                                    type="password"
                                    label="Password"
                                    variant="outlined"
                                    fullWidth
                                    margin="normal"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    required
                                />
                                <Button
                                    type="submit"
                                    variant="contained"
                                    color="primary"
                                    fullWidth
                                    sx={{ mt: 2 }}
                                >
                                    Login
                                </Button>
                            </form>
                        </div>
                    </div>
                ) : (
                    <div>
                        <h2>Welcome, {currentUser?.email}!</h2>

                        {/* Shopping Cart */}
                        <div className="cart-container">
                            <h3>Shopping Cart</h3>
                            {cart.size === 0 ? (
                                <p>Your cart is empty</p>
                            ) : (
                                <>
                                    {cartItems.map(({ product, quantity }) => (
                                        product && (
                                            <div key={product.id} className="cart-item">
                                                <span>{product.name}</span>
                                                <span>Qty: {quantity}</span>
                                                <span>${(Number(product.price) * quantity).toFixed(2)}</span>
                                                <Button
                                                    variant="contained"
                                                    size="small"
                                                    onClick={() => addToCart(product.id)}
                                                >
                                                    +
                                                </Button>
                                                <Button
                                                    variant="outlined"
                                                    size="small"
                                                    onClick={() => removeFromCart(product.id)}
                                                >
                                                    -
                                                </Button>
                                            </div>
                                        )
                                    ))}
                                    <div className="cart-total">
                                        <strong>Total: ${cartTotal.toFixed(2)}</strong>
                                    </div>
                                    <Button
                                        onClick={handlePlaceOrder}
                                        variant="contained"
                                        color="success"
                                        fullWidth
                                        sx={{ mt: 2 }}
                                    >
                                        Place Order
                                    </Button>
                                </>
                            )}
                        </div>

                        {/* Orders List */}
                        <div className="orders-container">
                            <h2>Your Orders</h2>
                            {orders.length === 0 ? (
                                <p>No orders yet</p>
                            ) : (
                                orders.map(order => (
                                <div key={order.id} className="order-card">
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                        <h3>Order #{order.id}</h3>
                                        {getStatusChip(order.status)}
                                    </div>
                                    <p><strong>Total: ${order.items.reduce((sum: number, item: any) =>
                                        sum + (Number(item.price_at_purchase) * item.quantity), 0
                                    ).toFixed(2)}</strong></p>

                                    <div className="order-items">
                                        {order.items.map((item: any, idx: number) => (
                                            <div key={item.id || idx} className="order-item">
                                                <span className="order-item-name">Product ID: {item.product_id}</span>
                                                <span className="order-item-qty">Qty: {item.quantity}</span>
                                                <span className="order-item-price">${Number(item.price_at_purchase).toFixed(2)}</span>
                                            </div>
                                        ))}
                                    </div>

                                    {order.status === 'pending' && (
                                        <Button
                                            variant="contained"
                                            color="success"
                                            fullWidth
                                            sx={{ mt: 2 }}
                                            onClick={() => handlePayNow(order)}
                                        >
                                            Pay Now
                                        </Button>
                                    )}
                                </div>
                                ))
                            )}
                        </div>
                    </div>
                )}

                {/* Payment Modal */}
                {selectedOrder && clientSecret && (
                    <>
                        <div className="payment-modal-overlay" onClick={() => {
                            setSelectedOrder(null);
                            setClientSecret(null);
                        }} />
                        <div className="payment-modal">
                            <h3>Pay for Order #{selectedOrder.id}</h3>
                            <Elements stripe={stripePromise}>
                                <PaymentForm
                                    clientSecret={clientSecret}
                                    onSuccess={() => {
                                        alert('Payment successful!');
                                        fetch(`${process.env.REACT_APP_API_URL}/orders/${selectedOrder.id}/process-payment`, {
                                            method: 'POST',
                                            headers: {
                                                'Authorization': `Bearer ${token}`,
                                            }
                                        }).then(res => res.json())
                                          .then(data => console.log('Order processed:', data));

                                        setSelectedOrder(null);
                                        setClientSecret(null);
                                        handleGetOrders();
                                    }}
                                    onCancel={() => {
                                        setSelectedOrder(null);
                                        setClientSecret(null);
                                    }}
                                />
                            </Elements>
                        </div>
                    </>
                )}
            </main>

            <hr />

            {/* Products Section */}
            <section className="inventory-section">
                <h2>Our Products</h2>
                <div className="product-grid">
                    {products.map(product => (
                        <div key={product.id} className="product-card">
                            <h3>{product.name}</h3>
                            <p>{product.description}</p>
                            <p className="price">${Number(product.price).toFixed(2)}</p>
                            <p className="inventory">In stock: {product.inventory_count}</p>
                            {token && (
                                <Button
                                    variant="contained"
                                    color="primary"
                                    onClick={() => addToCart(product.id)}
                                >
                                    Add to Cart
                                </Button>
                            )}
                        </div>
                    ))}
                </div>
            </section>
        </div>
    );
}

export default App;