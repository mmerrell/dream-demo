# Flower Shop Android App - Quick Setup Guide

## Prerequisites

1. **Android Studio**: Download and install Android Studio Hedgehog (2023.1.1) or later
2. **JDK 17**: Android Studio includes this
3. **Android SDK**: Install via Android Studio SDK Manager
   - Minimum API Level: 24 (Android 7.0)
   - Target API Level: 34 (Android 14)

## Quick Start (5 Minutes)

### Step 1: Configure Backend URL

Edit `app/build.gradle.kts` and update the backend URL:

```kotlin
// For Android Emulator (localhost on your machine)
buildConfigField("String", "API_BASE_URL", "\"http://10.0.2.2:8000\"")

// For Physical Device (replace with your computer's IP)
buildConfigField("String", "API_BASE_URL", "\"http://192.168.1.100:8000\"")
```

**Finding your computer's IP:**
- **Mac/Linux**: `ifconfig | grep inet`
- **Windows**: `ipconfig`

### Step 2: Configure Stripe

1. Get your Stripe **Publishable Key** from: https://dashboard.stripe.com/test/apikeys
2. Edit `app/build.gradle.kts`:

```kotlin
buildConfigField("String", "STRIPE_PUBLISHABLE_KEY", "\"pk_test_YOUR_KEY_HERE\"")
```

### Step 3: Open Project

1. Launch Android Studio
2. Click "Open" and select the `android-app` folder
3. Wait for Gradle sync to complete (may take a few minutes first time)

### Step 4: Start Backend Server

Make sure your backend is running:

```bash
cd backend
python -m uvicorn app.main:app --reload
```

Verify it's working: http://localhost:8000

### Step 5: Run the App

1. Click the "Run" button (▶️) in Android Studio toolbar
2. Select an emulator or connected device
3. Wait for the app to build and install

**First Time Emulator Setup:**
- Tools → Device Manager → Create Device
- Select "Pixel 5" or similar
- Download system image (API 34 recommended)
- Click "Finish"

## Testing the App

### Test Account
You can create a new account in the app, or use:
- Email: Any valid email format
- Password: Any password (at least 1 character)

### Test Payment (Stripe)
Use these test card numbers:
- **Success**: `4242 4242 4242 4242`
- **Decline**: `4000 0000 0000 0002`
- **Requires Auth**: `4000 0025 0000 3155`

Expiry: Any future date (e.g., 12/34)  
CVC: Any 3 digits (e.g., 123)

## Common Issues & Solutions

### 1. "Unable to connect to server"

**Problem**: App can't reach the backend

**Solutions**:
- ✅ Verify backend is running: `curl http://localhost:8000`
- ✅ For emulator: Use `10.0.2.2` not `localhost`
- ✅ For physical device: 
  - Ensure device and computer on same WiFi
  - Use computer's IP address in `API_BASE_URL`
  - Disable firewall or allow port 8000

### 2. "Build failed" or Gradle errors

**Solutions**:
- ✅ Clean project: `Build → Clean Project`
- ✅ Invalidate caches: `File → Invalidate Caches → Invalidate and Restart`
- ✅ Check internet connection (Gradle downloads dependencies)
- ✅ Update Gradle: `File → Project Structure → Project → Gradle Version`

### 3. Emulator is slow

**Solutions**:
- ✅ Enable hardware acceleration (HAXM on Intel, Hypervisor on M1/M2 Mac)
- ✅ Allocate more RAM to emulator (Device Manager → Edit → Show Advanced)
- ✅ Use a device with lower screen resolution

### 4. "Stripe key invalid"

**Solutions**:
- ✅ Ensure you're using the **Publishable Key** (starts with `pk_test_`)
- ✅ Not the Secret Key (which starts with `sk_test_`)
- ✅ Check for extra quotes or spaces in build.gradle.kts

## App Structure

```
📱 Flower Shop App
├── 🔐 Auth Screen (Login/Register)
├── 🏠 Home Screen
│   ├── Welcome message
│   ├── Product list
│   └── Add to cart
├── 🛒 Cart Screen
│   ├── Cart items with quantities
│   ├── Adjust quantities
│   └── Place order button
├── 📦 Orders Screen
│   ├── Filter orders by status
│   ├── View order details
│   ├── Pay pending orders
│   └── Cancel pending orders
└── 💳 Payment Screen
    └── Stripe payment sheet
```

## Development Tips

### Hot Reload
- Jetpack Compose supports live preview
- Open any `Screen.kt` file
- Click "Split" or "Design" button (top right)
- See UI changes in real-time without running the app

### Debugging
- Add breakpoints by clicking line numbers
- Use `Log.d("TAG", "message")` for logging
- View logs in "Logcat" tab (bottom of Android Studio)

### Testing API Calls
- Check "Logcat" and filter by "OkHttp" to see all API requests/responses
- Backend logs will show incoming requests

## Building for Release

### Create Signed APK

1. `Build → Generate Signed Bundle/APK`
2. Select "APK"
3. Create or select keystore
4. Choose "release" build variant
5. Find APK in `app/build/outputs/apk/release/`

**Security Note**: Never commit your keystore file to git!

## Project Architecture

- **MVVM Pattern**: Model-View-ViewModel
- **Dependency Injection**: Hilt
- **Networking**: Retrofit + OkHttp
- **UI**: Jetpack Compose
- **Navigation**: Navigation Compose
- **State Management**: StateFlow
- **Async**: Kotlin Coroutines

## Next Steps

- [ ] Customize app icon (replace files in `res/mipmap-*`)
- [ ] Add product images
- [ ] Implement push notifications
- [ ] Add biometric authentication
- [ ] Support dark mode improvements
- [ ] Add unit tests

## Need Help?

- **Android Studio Issues**: https://developer.android.com/studio/intro
- **Jetpack Compose**: https://developer.android.com/jetpack/compose/tutorial
- **Stripe Android**: https://stripe.com/docs/payments/accept-a-payment?platform=android
- **Retrofit**: https://square.github.io/retrofit/

## Version Info

- Kotlin: 1.9.10
- Compose: 2023.10.01
- Gradle: 8.2
- Min SDK: 24 (Android 7.0)
- Target SDK: 34 (Android 14)

