# simulate_orders.py
import asyncio
import aiohttp
import random
from datetime import datetime

# Configuration
API_URL = "http://localhost:8000"
NUM_ORDERS = 5  # Number of concurrent orders to simulate

# Test credentials (update with your test user)
EMAIL = "mmerrell@gmail.com"
PASSWORD = "a"


async def login(session):
    """Login and get auth token"""
    login_data = aiohttp.FormData()
    login_data.add_field('username', EMAIL)
    login_data.add_field('password', PASSWORD)

    async with session.post(f"{API_URL}/token", data=login_data) as resp:
        if resp.status != 200:
            error_text = await resp.text()
            print(f"❌ Login failed (status {resp.status}): {error_text}")
            raise Exception(f"Login failed: {error_text}")

        data = await resp.json()
        if 'access_token' not in data:
            print(f"❌ Unexpected response: {data}")
            raise Exception(f"No access_token in response: {data}")

        return data['access_token']

async def get_products(session, token):
    """Get available products"""
    headers = {'Authorization': f'Bearer {token}'}
    async with session.get(f"{API_URL}/products/", headers=headers) as resp:
        return await resp.json()


async def place_order(session, token, products, order_num):
    """Place order AND trigger payment processing"""
    # Randomly select 1-5 products
    num_items = random.randint(1, min(5, len(products)))
    selected_products = random.sample(products, num_items)

    # Build order
    order_data = {
        "items": [
            {
                "product_id": product['id'],
                "quantity": random.randint(1, 3)
            }
            for product in selected_products
        ]
    }

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    start_time = datetime.now()
    async with session.post(f"{API_URL}/orders/", json=order_data, headers=headers) as resp:
        duration = (datetime.now() - start_time).total_seconds()
        result = await resp.json()

        if resp.status == 200:
            print(f"✅ Order {order_num}: {result.get('workflow_id')} - {duration:.2f}s")
        else:
            print(f"❌ Order {order_num} failed: {result} - {duration:.2f}s")

    async with session.post(f"{API_URL}/orders/", json=order_data, headers=headers) as resp:
        if resp.status == 200:
            result = await resp.json()
            order_id = result.get('order_id')  # Or however you get it from response

            # NOW trigger payment processing
            async with session.post(
                    f"{API_URL}/orders/{order_id}/process-payment",
                    headers=headers
            ) as payment_resp:
                if payment_resp.status == 200:
                    print(f"✅ Order {order_num}: Created and processing started")
                else:
                    print(f"⚠️ Order {order_num}: Created but payment failed to start")
        else:
            print(f"❌ Order {order_num}: Failed to create")

        return result


async def main():
    print(f"🚀 Simulating {NUM_ORDERS} concurrent orders...")
    print(f"📍 API: {API_URL}")
    print(f"👤 User: {EMAIL}\n")

    async with aiohttp.ClientSession() as session:
        # Login
        print("🔐 Logging in...")
        token = await login(session)
        print("✅ Logged in!\n")

        # Get products
        print("📦 Fetching products...")
        products = await get_products(session, token)
        print(f"✅ Found {len(products)} products\n")

        # Place orders concurrently
        print(f"🛒 Placing {NUM_ORDERS} orders concurrently...\n")
        start_time = datetime.now()

        tasks = [
            place_order(session, token, products, i + 1)
            for i in range(NUM_ORDERS)
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        duration = (datetime.now() - start_time).total_seconds()

        # Summary
        successful = sum(1 for r in results if isinstance(r, dict) and 'workflow_id' in r)
        print(f"\n{'=' * 50}")
        print(f"📊 Results:")
        print(f"   Total orders: {NUM_ORDERS}")
        print(f"   Successful: {successful}")
        print(f"   Failed: {NUM_ORDERS - successful}")
        print(f"   Total time: {duration:.2f}s")
        print(f"   Avg time per order: {duration / NUM_ORDERS:.2f}s")
        print(f"{'=' * 50}")



if __name__ == "__main__":
    # First, make sure you have a test user registered
    print("⚠️  Make sure you have registered test@example.com first!\n")
    asyncio.run(main())