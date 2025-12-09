# Quick Start - Android App

## Backend is Already Running! ✅
- Backend: http://localhost:8000
- Database: Seeded with 300 products
- Stripe: Configured

## Option 1: Run in Android Studio (Easiest)

### 1. Open Android Studio
```bash
# Open the android-app folder in Android Studio
open -a "Android Studio" /Users/adam.toth-fejel/Documents/GitHub/dream-demo/android-app
```

### 2. Configure Backend URL

The app is already configured for emulator:
- **Emulator**: `http://10.0.2.2:8000` (maps to your localhost:8000)
- **Physical Device**: Need to use your Mac's IP address

**To find your Mac's IP:**
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

If using a physical device, update `android-app/app/build.gradle.kts`:
```kotlin
buildConfigField("String", "API_BASE_URL", "\"http://YOUR_IP:8000\"")
```

### 3. Configure Stripe Key (Already Done!)
The test Stripe key is already configured in `app/build.gradle.kts`

### 4. Run the App
1. Click the green "Run" button (▶️) in Android Studio
2. Select an emulator or connected device
3. Wait for build and installation

## Option 2: Command Line Build

### Build APK
```bash
cd /Users/adam.toth-fejel/Documents/GitHub/dream-demo/android-app
./gradlew assembleDebug
```

APK will be at: `app/build/outputs/apk/debug/app-debug.apk`

### Install on Device
```bash
# If you have adb installed
adb install app/build/outputs/apk/debug/app-debug.apk
```

## Testing the App

1. **Register** a new account (any email/password)
2. **Browse** 300 flower products
3. **Add to cart** and adjust quantities
4. **Place order**
5. **Pay** with Stripe test card: `4242 4242 4242 4242`
   - Expiry: Any future date (12/34)
   - CVC: Any 3 digits (123)

## Troubleshooting

### "Cannot connect to server"
- **Emulator**: Should work with `10.0.2.2:8000`
- **Physical Device**: 
  1. Mac and phone on same WiFi
  2. Use Mac's IP address in build.gradle.kts
  3. Rebuild app

### Gradle sync issues
1. File → Invalidate Caches → Restart
2. Build → Clean Project
3. Build → Rebuild Project

## What's Different from Web?

- **Native Android UI** with Material 3
- **Better performance** (native code)
- **Offline capable** (can be added)
- **Android-specific features** (push notifications, etc.)

## Current Features

✅ User registration & login
✅ Browse 300 products
✅ Shopping cart management
✅ Order creation & tracking
✅ Order filtering (6 statuses)
✅ Stripe payment integration
✅ Cancel pending orders
✅ Beautiful Material 3 Design

