# Known Bugs & Issues

This document tracks known bugs in the Dream Demo Flower Shop application. These bugs are intentionally left in the codebase for testing and debugging exercises.

## Bug List

### Intrusive Alert Dialogs for User Actions
- **Status**: 🔴 Unfixed
- **Severity**: Medium
- **Component**: Frontend - User Experience
- **Description**: The application uses native browser `alert()` dialogs for user feedback (order placement, payment success, login success, registration failures, etc.). These are intrusive, block all interaction, and provide poor UX. They're modal, unstyled, and inconsistent with the modern Material-UI design system used elsewhere in the app.
- **Location**: `frontend-web/src/App.tsx` - Multiple functions including `handlePlaceOrder()`, `handleRegister()`, `handleLogin()`, `handlePayNow()`, and payment success callback
- **Reproduction Steps**:
  1. Add items to cart and click "Place Order"
  2. Observe blocking alert dialog "Order placed successfully!"
  3. Must click OK to dismiss before doing anything else
- **Expected Behavior**: Should use non-blocking notifications like MUI Snackbar or Toast notifications that appear briefly and auto-dismiss, allowing users to continue interacting with the app
- **Current Behavior**: Uses `alert()` which blocks all user interaction until dismissed
- **Affected Actions**:
  - Order placement success
  - Payment success
  - Login success
  - Registration failure
  - Session expiration
  - Payment initiation failure
  - Order placement failure
- **Potential Fixes**: 
  - Replace all `alert()` calls with MUI Snackbar component
  - Implement a toast notification system
  - Use inline success/error messages near the action buttons
  - Add a notification queue for multiple messages
---

### Payment Fails for $0 Orders
- **Status**: 🔴 Unfixed
- **Severity**: Medium
- **Component**: Backend - Payment Processing
- **Description**: $0 orders created by inventory bugs show "Failed to initiate payment" but remain in the orders list forever
- **Location**: Backend - `main.py` create_payment_intent
- **Reproduction Steps**:
  1. Create a $0 order (via inventory bug)
  2. Try to pay for it
  3. Get "Failed to initiate payment" alert
  4. Order remains in pending state indefinitely
- **Expected Behavior**: Either prevent $0 orders from being created, or auto-cancel them, or allow deletion
- **Current Behavior**: $0 orders stuck in pending state forever with no way to remove them

### No Order Management - Cannot Delete/Cancel Orders
- **Status**: 🟡 Partially Fixed
- **Severity**: Medium
- **Component**: Frontend - Order Management
- **Description**: Users cannot delete, cancel, or modify orders once created. Invalid/test orders accumulate with no cleanup mechanism.
- **Location**: `frontend-web/src/App.tsx` - Orders display section
- **Reproduction Steps**:
  1. Create any order
  2. Observe no delete/cancel options available
  3. Order remains in list permanently
- **Expected Behavior**: 
  - Pending orders should have "Cancel" button
  - Cancelled/completed orders should be hideable/filterable
  - Admin/user should be able to delete invalid orders
- **Current Behavior**: All orders displayed permanently with no management options

### Email Already Registered - Poor Error Feedback
- **Status**: ✅ Fixed
- **Severity**: Medium
- **Component**: Frontend - User Registration
- **Description**: When attempting to register with an email that's already in use, the user receives a generic browser alert with no helpful guidance. The error handling doesn't differentiate between network errors, validation errors, and duplicate email errors, providing a poor user experience.
- **Location**: `frontend-web/src/App.tsx` - `handleRegister()` function
- **Reproduction Steps**:
  1. Register a new account with email `test@example.com`
  2. Try to register again with the same email
  3. Observe generic `alert('Registration failed.')` message
- **Expected Behavior**: Should display a clear, user-friendly message like "This email is already registered. Would you like to log in instead?" and potentially redirect to login or offer to recover password
- **Current Behavior**: Shows generic alert "Registration failed." with no indication of what went wrong or how to fix it
- **Backend Response**: Returns 400 with `{"detail": "Email already registered"}` which is being ignored
- **Potential Fixes**: 
  - Parse the error response and show specific error messages
  - Add inline form validation showing "Email already in use"
  - Offer quick link to login form for existing users
  - Use MUI Snackbar/Alert instead of browser alerts for better UX

### Inventory Exceeds Available Stock - Poor Error Handling
- **Status**: ✅ Fixed
- **Severity**: High
- **Component**: Backend/Frontend - Order Creation
- **Description**: When placing an order that exceeds available inventory, the system creates a $0 order with 0 quantity items and only shows generic "Failed to place order" alert. The phantom order doesn't appear until page refresh.
- **Location**: Backend - `crud.py` order creation, Frontend - `App.tsx` handlePlaceOrder
- **Reproduction Steps**:
  1. Find a product with limited inventory (e.g., 5 in stock)
  2. Add 10 of that item to cart
  3. Click "Place Order"
  4. Observe generic error alert
  5. Refresh page - see $0 order created
- **Expected Behavior**: Should validate inventory before creating order, show specific error message about which items are out of stock, prevent order creation
- **Current Behavior**: Creates invalid $0 order, generic error message, order not visible until refresh

## Testing Notes

This application is intentionally left with bugs for educational purposes. When writing automated tests:
- Test both happy paths and error cases
- Verify error handling and user feedback
- Check edge cases (long inputs, empty states, etc.)
- Test authentication flows thoroughly
- Validate data types between frontend and backend

## Contributing

When you find a new bug, please add it to this document with:
- Clear description
- Steps to reproduce
- Expected vs actual behavior
- Component/file location
- Severity assessment