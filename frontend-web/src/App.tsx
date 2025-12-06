import { useState, useEffect, FormEvent, useCallback } from 'react';
import React from 'react';
import { getProducts } from './services/productService';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Chip from '@mui/material/Chip';
import { Elements } from '@stripe/react-stripe-js';
import { loadStripe } from '@stripe/stripe-js';
import { useSnackbar } from './contexts/SnackbarContext';
import axios from 'axios';
import { ErrorBoundary } from './components/ErrorBoundary';
import ShoppingCartDrawer from './components/ShoppingCartDrawer';
import OrderStatusCard from './components/OrderStatusCard';

import {
    register,
    login,
    getCurrentUser,
    createOrder,
    getOrders,
    createPaymentIntent,
    User,
    OrderItemCreate,
    cancelOrder
} from './services/apiService';
import { Product } from './services/productService';
import PaymentForm from './components/PaymentForm';
import './App.css';
import EnhancedProductGrid from "./EnhancedProductGrid";

const getSprintStyling = (sprintVersion: string) => {
  const sprintConfig = {
    'sprint-1': {
      adjective: 'Dreadful',
      style: {
        fontFamily: 'Comic Sans MS, cursive',
        color: '#ff0066',                   // Bright pink
        textShadow: '2px 2px 4px #000'
      }
    },
    'sprint-2': {
      adjective: 'Clunky',
      style: {
        fontFamily: 'Arial Black, sans-serif',
        color: '#ff8c00',                   // Bright orange
        letterSpacing: '2px'
      }
    },
    'sprint-3': {
      adjective: 'Tolerable',
      style: {
        fontFamily: 'Georgia, serif',
        color: '#e0e0e0',                   // Light gray
        fontWeight: 'normal'
      }
    },
    'sprint-4': {
      adjective: 'Decent',
      style: {
        fontFamily: 'Helvetica, Arial, sans-serif',
        color: '#ffffff',                   // Clean white
        fontWeight: '600'
      }
    }
    // Future sprints can get progressively more elegant
  };
  return sprintConfig[sprintVersion as keyof typeof sprintConfig] || sprintConfig['sprint-1'];
};

const sprintVersion = process.env.REACT_APP_SPRINT_VERSION || 'dev';
const { adjective, style } = getSprintStyling(sprintVersion);

const SprintBadge = () => {
  const sprintConfig: Record<string, { emoji: string; name: string; color: string }> = {
    'sprint-1': { emoji: '🌹', name: 'sprint-1', color: '#e74c3c' },
    'sprint-2': { emoji: '🌸', name: 'sprint-2', color: '#ff6b9d' },
    'sprint-3': { emoji: '🌻', name: 'sprint-3', color: '#f39c12' },
    'sprint-4': { emoji: '🌺', name: 'sprint-4', color: '#e91e63' },
    'sprint-5': { emoji: '🌷', name: 'sprint-5', color: '#9b59b6' },
    'sprint-6': { emoji: '🌼', name: 'sprint-6', color: '#f1c40f' },
    'sprint-7': { emoji: '🌿', name: 'sprint-7', color: '#27ae60' },
    'sprint-8': { emoji: '🌾', name: 'sprint-8', color: '#d4af37' },
    'sprint-9': { emoji: '🏵️', name: 'sprint-9', color: '#fd79a8' },
    'sprint-10': { emoji: '🌰', name: 'Sprint-10', color: '#8b4513' },
    'dev': { emoji: '🛠️', name: 'dev', color: '#34495e' }
  };

  const config = sprintConfig[sprintVersion as keyof typeof sprintConfig] || sprintConfig['dev'];

  const githubBranch = sprintVersion === 'dev' ? 'main' : sprintVersion;
  const githubUrl = `https://github.com/mmerrell/dream-demo/tree/${githubBranch}`;

  return (
    <a
      href={githubUrl}
      target="_blank"
      rel="noopener noreferrer"
      style={{
        position: 'fixed',
        bottom: '15px',
        right: '15px',
        backgroundColor: config.color,
        color: 'white',
        padding: '8px 12px',
        borderRadius: '20px',
        fontSize: '12px',
        fontWeight: 'bold',
        zIndex: 1000,
        boxShadow: '0 3px 10px rgba(0,0,0,0.2)',
        display: 'flex',
        alignItems: 'center',
        gap: '5px',
        cursor: 'pointer',
        transition: 'transform 0.2s ease',
        userSelect: 'none',
        textDecoration: 'none'
      }}
      onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.05)'}
      onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1.0)'}
      title={`View ${config.name} branch on GitHub`}
    >
      <span style={{ fontSize: '14px' }}>{config.emoji}</span>
      <span>{config.name}</span>
    </a>
  );
};

console.log('About to call loadStripe with:', process.env.REACT_APP_STRIPE_PUBLISHABLE_KEY);
const stripePromise = loadStripe(process.env.REACT_APP_STRIPE_PUBLISHABLE_KEY!);
console.log('loadStripe result:', stripePromise);

function App() {
   useEffect(() => {
      console.log('Stripe key check:', {
        key: process.env.REACT_APP_STRIPE_PUBLISHABLE_KEY,
        keyLength: process.env.REACT_APP_STRIPE_PUBLISHABLE_KEY?.length,
        keyType: typeof process.env.REACT_APP_STRIPE_PUBLISHABLE_KEY
      });
    }, []);

    // App State
    const [products, setProducts] = useState<Product[]>([]);
    const [cart, setCart] = useState<Map<number, number>>(new Map());
    const [orders, setOrders] = useState<any[]>([]);
    const [cartOpen, setCartOpen] = useState(false);

    // Payment State
    const [selectedOrder, setSelectedOrder] = useState<any | null>(null);
    const [clientSecret, setClientSecret] = useState<string | null>(null);

    // Snackbar Notifications
    const { showSnackbar } = useSnackbar();

    // Auth State
    const [token, setToken] = useState<string | null>(
        localStorage.getItem('authToken')  // <-- Updated this line
    );
    const [currentUser, setCurrentUser] = useState<User | null>(null);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');

    const handleGetMe = useCallback(async () => {
        if (!token) return;
        try {
            setCurrentUser(await getCurrentUser(token));
        }
        catch (error) {
            showSnackbar('Session expired. Please log in again.', 'error');
            setToken(null);
            localStorage.removeItem('authToken');
        }
    }, [token, showSnackbar]);

    const handleGetOrders = useCallback(async () => {
        if (!token) return;
        try { setOrders(await getOrders(token)); }
        catch (error) { console.error("Failed to fetch orders", error); }
    }, [token]);

    useEffect(() => {
        fetchProducts();
    }, []);

    useEffect(() => {
        if (token) {
            handleGetMe();
            handleGetOrders();
        }
    }, [token, handleGetMe, handleGetOrders]);

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
            showSnackbar('Success! Please log in.', 'success');
            setEmail('');
            setPassword('');
        }
        catch (error: any) {
            let errorMessage = 'Registration failed.';
            if (axios.isAxiosError(error)) {
                if (error.response?.data?.detail) {
                    errorMessage = error.response.data.detail;
                }
            }
            else if (error instanceof Error) {
                errorMessage = error.message;
            }
            showSnackbar(errorMessage, 'error');
        }
    };

    const handleLogin = async (e: FormEvent) => {
        e.preventDefault();
        const formData = new FormData();
        formData.append('username', email);
        formData.append('password', password);
        try {
            const res = await login(formData);
            setToken(res.access_token);
            localStorage.setItem('authToken', res.access_token);
            showSnackbar('Login successful!', 'success');
        }
        catch (error) { showSnackbar('Login failed.', 'error'); }
    };

    const handlePlaceOrder = async () => {
        if (!token || cart.size === 0) return;
        const orderItems: OrderItemCreate[] = Array.from(cart.entries()).map(([pid, q]) => ({ product_id: pid, quantity: q }));
        try {
            await createOrder({ items: orderItems }, token);
            showSnackbar('Order placed successfully!', 'success');
            setCart(new Map());
            handleGetOrders();
        }
        catch (error) {
            let errorMessage = 'Could not place order. ';
            if (axios.isAxiosError(error)) {
                if (error.response?.data?.detail) {
                    errorMessage += error.response.data.detail;
                }
            }
            else if (error instanceof Error) {
                errorMessage += error.message;
            }
            showSnackbar(errorMessage, 'error');
        }
    };

    const handlePayNow = async (order: any) => {
        if (!token) return;
        try {
            const res = await createPaymentIntent(order.id, token);
            setClientSecret(res.client_secret);
            setSelectedOrder(order);
        } catch (error) {
            showSnackbar('Failed to initiate payment.', 'error');
        }
    };

    const handleCancelOrder = async (orderId: number) => {
        if (!token) return;
        if (!window.confirm('Are you sure you want to cancel this order?')) return;

        try {
            await cancelOrder(orderId, token);
            showSnackbar('Order cancelled successfully', 'success');
            handleGetOrders();
        } catch (error) {
            showSnackbar('Failed to cancel order', 'error');
        }
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

    const [orderFilters, setOrderFilters] = useState({
        pending: true,
        paid: true,
        processing: true,
        completed: false,
        cancelled: false,
        payment_failed: false
    });

    const triggerError = () => {
      if (Math.random() > 0.8) {
        throw new Error(`Sprint ${sprintVersion} demo error`);
      }
    };
    (window as any).triggerError = triggerError;

    const toggleFilter = (status: keyof typeof orderFilters) => {
        setOrderFilters(prev => ({
            ...prev,
            [status]: !prev[status]
        }));
    };

    // Filter orders
    const visibleOrders = orders.filter(order =>
        orderFilters[order.status as keyof typeof orderFilters]
    );

    return (
        <ErrorBoundary sprintVersion={sprintVersion}>
            <div className="App">
                <SprintBadge />
                <header className="App-header">
                    <div className="header-left">
                        <img src="/logo.png" alt="Flower Shop Logo" className="logo" />
                        <h1 style={style}>{adjective} Flower Shop</h1>
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
                            aria-label="Logout from your account"
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
                                <form onSubmit={handleRegister} aria-label="Registration form">
                                    <TextField
                                        type="email"
                                        label="Email"
                                        variant="outlined"
                                        fullWidth
                                        margin="normal"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        required
                                        InputProps={{
                                            inputProps: { 'aria-label': 'Email address for registration' }
                                        }}
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
                                        InputProps={{
                                            inputProps: { 'aria-label': 'Password for registration' }
                                        }}
                                    />
                                    <Button
                                        type="submit"
                                        variant="contained"
                                        color="primary"
                                        fullWidth
                                        sx={{ mt: 2 }}
                                        aria-label="Submit registration"
                                    >
                                        Register
                                    </Button>
                                </form>
                            </div>
                            <div className="auth-form">
                                <h2>Login</h2>
                                <form onSubmit={handleLogin} aria-label="Login form">
                                    <TextField
                                        type="email"
                                        label="Email"
                                        variant="outlined"
                                        fullWidth
                                        margin="normal"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        required
                                        InputProps={{
                                            inputProps: { 'aria-label': 'Email address for login' }
                                        }}
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
                                        InputProps={{
                                            inputProps: { 'aria-label': 'Password for login' }
                                        }}
                                    />
                                    <Button
                                        type="submit"
                                        variant="contained"
                                        color="primary"
                                        fullWidth
                                        sx={{ mt: 2 }}
                                        aria-label="Submit login"
                                    >
                                        Login
                                    </Button>
                                </form>
                            </div>
                        </div>
                    ) : (
                        <div>
                            <h2>Welcome, {currentUser?.email}!</h2>

                            {/* Shopping Cart - just a button to open drawer */}
                            <Button
                              variant="contained"
                              onClick={() => setCartOpen(true)}
                              sx={{ mb: 2 }}
                            >
                              🛒 Cart ({cart.size})
                            </Button>

                            {/* Shopping Cart Drawer */}
                            <ShoppingCartDrawer
                              open={cartOpen}
                              onClose={() => setCartOpen(false)}
                              items={(cartItems as any).map((item: any) => ({
                                id: item.product?.id || 0,
                                name: item.product?.name || '',
                                price: Number(item.product?.price || 0),
                                quantity: item.quantity,
                                image_url: item.product?.image_url
                              }))}
                              onUpdateQuantity={(id, newQuantity) => {
                                // Update cart logic - you'll need to implement this
                              }}
                              onRemoveItem={(id) => {
                                // Remove item completely - implement this
                              }}
                              onCheckout={handlePlaceOrder}
                              loading={false}
                            />

                            {/* Orders List */}
                            <div className="orders-container">
                                <h2>Your Orders</h2>

                                {/* Filter Buttons */}
                                <div style={{
                                    display: 'flex',
                                    gap: '8px',
                                    marginBottom: '16px',
                                    flexWrap: 'wrap'
                                }}>
                                    <Button
                                        variant={orderFilters.pending ? "contained" : "outlined"}
                                        color="warning"
                                        size="small"
                                        onClick={() => toggleFilter('pending')}
                                    >
                                        ⏳ Pending
                                    </Button>
                                    <Button
                                        variant={orderFilters.paid ? "contained" : "outlined"}
                                        color="info"
                                        size="small"
                                        onClick={() => toggleFilter('paid')}
                                    >
                                        💳 Paid
                                    </Button>
                                    <Button
                                        variant={orderFilters.processing ? "contained" : "outlined"}
                                        color="info"
                                        size="small"
                                        onClick={() => toggleFilter('processing')}
                                    >
                                        📦 Processing
                                    </Button>
                                    <Button
                                        variant={orderFilters.completed ? "contained" : "outlined"}
                                        color="success"
                                        size="small"
                                        onClick={() => toggleFilter('completed')}
                                    >
                                        ✓ Completed
                                    </Button>
                                    <Button
                                        variant={orderFilters.cancelled ? "contained" : "outlined"}
                                        color="error"
                                        size="small"
                                        onClick={() => toggleFilter('cancelled')}
                                    >
                                        ✗ Cancelled
                                    </Button>
                                    <Button
                                        variant={orderFilters.payment_failed ? "contained" : "outlined"}
                                        color="error"
                                        size="small"
                                        onClick={() => toggleFilter('payment_failed')}
                                    >
                                        ⚠ Payment Failed
                                    </Button>
                                </div>

                                {(() => {
                                    console.log('visibleOrders:', visibleOrders);
                                    return null;
                                })()}

                                {visibleOrders.length === 0 ? (
                                    <p>No orders to display</p>
                                ) : (
                                    visibleOrders.map(order => (
                                    <div key={order.id}>
                                        <h3>Order {order.id}</h3>
                                        <p>Status: {order.status}</p>
                                        <OrderStatusCard
                                            key={`card-${order.id}`}
                                            order={order}
                                            onPayOrder={handlePayNow}
                                            onCancelOrder={handleCancelOrder}
                                            loading={false}
                                        />
                                    </div>
                                    ))
                                )}
                            </div>
                        </div>
                    )}

                    {/* Payment Modal */}
                    {selectedOrder && clientSecret && (
                        <>
                            <div className="payment-modal-overlay"
                                 onClick={() => {
                                     setSelectedOrder(null);
                                     setClientSecret(null);
                                 }}
                                 aria-label="Close payment modal"
                                 role="button"
                                 tabIndex={0}
                            />
                            <div className="payment-modal"
                                role="dialog"
                                aria-labelledby="payment-modal-title"
                                aria-describedby="payment-modal-description"
                            >
                                <h3 id="payment-modal-title">Pay for Order #{selectedOrder.id}</h3>
                                <p id="payment-modal-description" className="sr-only">
                                    Enter your payment information to complete your order
                                </p>

                                <Elements stripe={stripePromise}>
                                    <PaymentForm
                                        clientSecret={clientSecret}
                                        onSuccess={() => {
                                            showSnackbar('Payment successful!', 'success');
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
                <EnhancedProductGrid
                  products={products}
                  onAddToCart={(product) => addToCart(product.id)}
                />
            </div>
        </ErrorBoundary>
    );
}

export default App;