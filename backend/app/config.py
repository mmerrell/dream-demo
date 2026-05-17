import os

# --- Stripe & Sauce Labs config (Test Environment) ---
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "YOUR_STRIPE_PUBLISHABLE_KEY")

SAUCE_USERNAME = os.getenv("SAUCE_USERNAME", "")
SAUCE_ACCESS_KEY = os.getenv("SAUCE_ACCESS_KEY", "")
SAUCE_REGION = os.getenv("SAUCE_REGION", "us-west-1")
SAUCE_API_HOST = f"https://api.{SAUCE_REGION}.saucelabs.com"

if not STRIPE_SECRET_KEY:
    print("WARNING: STRIPE_SECRET_KEY not set!")

if not SAUCE_USERNAME or not SAUCE_ACCESS_KEY:
    print("WARNING: SAUCE_USERNAME or SAUCE_ACCESS_KEY not set! AI Authoring endpoints will fail without them.")
