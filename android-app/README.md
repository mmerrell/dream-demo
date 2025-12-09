# Flower Shop Android App

A modern Android e-commerce application for a flower shop, built with Kotlin and Jetpack Compose.

## Features

- 🌸 **User Authentication**: Register and login with email/password
- 🛍️ **Product Browsing**: View available flowers with descriptions and prices
- 🛒 **Shopping Cart**: Add, remove, and manage items in your cart
- 📦 **Order Management**: Create and track orders with multiple status filters
- 💳 **Stripe Payment Integration**: Secure payment processing using Stripe
- 🎨 **Modern UI**: Built with Jetpack Compose and Material 3 Design

## Tech Stack

- **Language**: Kotlin
- **UI Framework**: Jetpack Compose
- **Architecture**: MVVM (Model-View-ViewModel)
- **Dependency Injection**: Hilt
- **Networking**: Retrofit + OkHttp
- **Async Operations**: Kotlin Coroutines + Flow
- **Local Storage**: DataStore
- **Payment**: Stripe Android SDK
- **Navigation**: Jetpack Navigation Compose

## Prerequisites

- Android Studio Hedgehog (2023.1.1) or later
- JDK 17
- Android SDK API 34
- Minimum Android SDK API 24

## Setup Instructions

### 1. Clone the Repository

```bash
cd android-app
```

### 2. Configure Backend URL

In `app/build.gradle.kts`, update the `API_BASE_URL`:

```kotlin
buildConfigField("String", "API_BASE_URL", "\"http://10.0.2.2:8000\"")
```

**Note**: 
- `10.0.2.2` is the special IP for localhost when using Android Emulator
- For physical devices, use your computer's IP address (e.g., `"http://192.168.1.100:8000"`)
- For production, use your actual backend URL

### 3. Configure Stripe

1. Get your Stripe publishable key from [Stripe Dashboard](https://dashboard.stripe.com/apikeys)
2. In `app/build.gradle.kts`, update:

```kotlin
buildConfigField("String", "STRIPE_PUBLISHABLE_KEY", "\"pk_test_your_key_here\"")
```

### 4. Sync Project

Open the project in Android Studio and sync Gradle files.

### 5. Run the App

1. Start your backend server (make sure it's running on port 8000)
2. Select an emulator or connect a physical device
3. Click Run (▶️) in Android Studio

## Project Structure

```
app/src/main/java/com/example/flowershop/
├── data/
│   ├── api/              # API service and interceptors
│   ├── local/            # Local data storage (DataStore)
│   ├── models/           # Data models
│   └── repository/       # Repository pattern implementations
├── di/                   # Dependency injection modules
├── ui/
│   ├── navigation/       # Navigation setup
│   ├── screens/          # Composable screens
│   ├── theme/            # App theme and styling
│   └── viewmodel/        # ViewModels
├── util/                 # Utility classes
├── FlowerShopApplication.kt
└── MainActivity.kt
```

## API Endpoints Used

The app communicates with the following backend endpoints:

- `POST /token` - User login
- `POST /users/` - User registration
- `GET /users/me/` - Get current user info
- `GET /products/` - Fetch all products
- `POST /orders/` - Create a new order
- `GET /orders/` - Get user's orders
- `POST /orders/{id}/cancel` - Cancel an order
- `POST /create-payment-intent` - Create Stripe payment intent
- `POST /orders/{id}/process-payment` - Process payment after Stripe confirmation

## Key Features Explanation

### Authentication Flow
- Users can register with email and password
- Login persists using DataStore
- JWT token is automatically attached to API requests via interceptor

### Shopping Cart
- Products can be added/removed from cart
- Cart state is managed in ProductViewModel
- Quantities can be adjusted before placing order

### Order Management
- Orders can be filtered by status (pending, paid, processing, completed, cancelled, payment_failed)
- Pending orders can be paid or cancelled
- Real-time status updates after payment

### Payment Flow
1. User clicks "Pay Now" on a pending order
2. App creates a payment intent via backend
3. Stripe Payment Sheet opens
4. After successful payment, backend processes the order
5. Order status updates to "paid" then "processing" then "completed"

## Testing

### Test Cards (Stripe Test Mode)

- **Success**: 4242 4242 4242 4242
- **Decline**: 4000 0000 0000 0002
- Use any future expiry date and any 3-digit CVC

## Troubleshooting

### Backend Connection Issues

1. Verify backend is running: `curl http://localhost:8000`
2. Check API_BASE_URL configuration
3. For emulator, ensure you're using `10.0.2.2` not `localhost`
4. For physical device, ensure both device and computer are on same network

### Build Issues

1. Clean project: `Build > Clean Project`
2. Invalidate caches: `File > Invalidate Caches > Invalidate and Restart`
3. Sync Gradle: `File > Sync Project with Gradle Files`

### Stripe Issues

1. Verify Stripe publishable key is correct
2. Check internet permissions in AndroidManifest.xml
3. Ensure using test mode keys for development

## Future Enhancements

- [ ] Product images support
- [ ] Product search and filtering
- [ ] Order history with detailed tracking
- [ ] Push notifications for order updates
- [ ] Multiple payment methods
- [ ] User profile management
- [ ] Wishlist functionality
- [ ] Product reviews and ratings

## License

This project is part of the Dream Demo application suite.

