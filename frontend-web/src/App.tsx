import React, { useState, useEffect, FormEvent, useCallback } from 'react';
import { getProducts } from './services/productService';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Chip from '@mui/material/Chip';
import { Elements } from '@stripe/react-stripe-js';
import { loadStripe } from '@stripe/stripe-js';
import { useSnackbar } from './contexts/SnackbarContext';
import axios from 'axios';
import { ErrorBoundary } from './components/ErrorBoundary';
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
        } catch (error) { showSnackbar('Failed to initiate payment.', 'error'); }
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
                                                        aria-label={`Increase quantity of ${product.name}`}
                                                    >
                                                        +
                                                    </Button>
                                                    <Button
                                                        variant="outlined"
                                                        size="small"
                                                        onClick={() => removeFromCart(product.id)}
                                                        aria-label={`Decrease quantity of ${product.name}`}
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
                                            aria-label={`Place order for ${cart.size} items totaling ${cartTotal.toFixed(2)}`}
                                        >
                                            Place Order
                                        </Button>
                                    </>
                                )}
                            </div>

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
                                        aria-label="Toggle pending orders"
                                    >
                                        ⏳ Pending
                                    </Button>
                                    <Button
                                        variant={orderFilters.paid ? "contained" : "outlined"}
                                        color="info"
                                        size="small"
                                        onClick={() => toggleFilter('paid')}
                                        aria-label="Toggle paid orders"
                                    >
                                        💳 Paid
                                    </Button>
                                    <Button
                                        variant={orderFilters.processing ? "contained" : "outlined"}
                                        color="info"
                                        size="small"
                                        onClick={() => toggleFilter('processing')}
                                        aria-label="Toggle processing orders"
                                    >
                                        📦 Processing
                                    </Button>
                                    <Button
                                        variant={orderFilters.completed ? "contained" : "outlined"}
                                        color="success"
                                        size="small"
                                        onClick={() => toggleFilter('completed')}
                                        aria-label="Toggle completed orders"
                                    >
                                        ✓ Completed
                                    </Button>
                                    <Button
                                        variant={orderFilters.cancelled ? "contained" : "outlined"}
                                        color="error"
                                        size="small"
                                        onClick={() => toggleFilter('cancelled')}
                                        aria-label="Toggle cancelled orders"
                                    >
                                        ✗ Cancelled
                                    </Button>
                                    <Button
                                        variant={orderFilters.payment_failed ? "contained" : "outlined"}
                                        color="error"
                                        size="small"
                                        onClick={() => toggleFilter('payment_failed')}
                                        aria-label="Toggle payment failed orders"
                                    >
                                        ⚠ Payment Failed
                                    </Button>
                                </div>

                                {visibleOrders.length === 0 ? (
                                    <p>No orders to display</p>
                                ) : (
                                    visibleOrders.map(order => (
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
                                                <div style={{ display: 'flex', gap: '8px', marginTop: '12px' }}>
                                                    <Button
                                                        variant="contained"
                                                        color="success"
                                                        fullWidth
                                                        onClick={() => handlePayNow(order)}
                                                        aria-label={`Pay now for order ${order.id} totaling ${order.items.reduce((sum: number, item: any) => 
                                                            sum + (Number(item.price_at_purchase) * item.quantity), 0
                                                        ).toFixed(2)}`}                                                >
                                                        Pay Now
                                                    </Button>
                                                    <Button
                                                        variant="outlined"
                                                        color="error"
                                                        fullWidth
                                                        onClick={() => handleCancelOrder(order.id)}
                                                        aria-label={`Cancel order ${order.id}`}
                                                    >
                                                        Cancel Order
                                                    </Button>
                                                </div>
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
                <section className="inventory-section">
                    <h2>Our Products</h2>
                    <div className="product-grid">
                        {products.map(product => (
                            <div key={product.id} className="product-card">
                                {product.image_url && (
                                    <div className="product-image">
                                      <img
                                        src={product.image_url || '/images/placeholder-flower.jpg'}
                                        alt={product.name}
                                        onError={(e) => {
                                          const img = e.target as HTMLImageElement;
                                          img.src = '/images/placeholder-flower.jpg';
                                        }}
                                      />
                                    </div>
                                )}
                                <h3>{product.name}</h3>
                                <p>{product.description}</p>
                                <p className="price">${Number(product.price).toFixed(2)}</p>
                                <p className="inventory" aria-label={`${product.inventory_count} items in stock`}>
                                    In stock: {product.inventory_count}</p>
                                {token && (
                                    <Button
                                        variant="contained"
                                        color="primary"
                                        onClick={() => addToCart(product.id)}
                                        aria-label={`Add ${product.name} to cart for ${Number(product.price).toFixed(2)}`}
                                    >
                                        Add to Cart
                                    </Button>
                                )}
                            </div>
                        ))}
                    </div>
                </section>
            </div>
        </ErrorBoundary>
    );
}

export default App;