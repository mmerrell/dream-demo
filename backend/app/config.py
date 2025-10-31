import os

# --- Stripe API Keys (Test Environment) ---
# For this demo, we are using placeholder keys.
# You can get your own test keys from the Stripe dashboard: https://dashboard.stripe.com/test/apikeys
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "YOUR_STRIPE_PUBLISHABLE_KEY")

if not STRIPE_SECRET_KEY:
    print("WARNING: STRIPE_SECRET_KEY not set!")
