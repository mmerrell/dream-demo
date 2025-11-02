# cancel_all_pending_orders.py
import asyncio
import aiohttp

API_URL = "http://localhost:8000"
EMAIL = "mmerrell@gmail.com"
PASSWORD = "a"


async def login(session):
    """Login and get auth token"""
    login_data = aiohttp.FormData()
    login_data.add_field('username', EMAIL)
    login_data.add_field('password', PASSWORD)

    async with session.post(f"{API_URL}/token", data=login_data) as resp:
        data = await resp.json()
        return data['access_token']


async def get_orders(session, token):
    """Get all orders"""
    headers = {'Authorization': f'Bearer {token}'}
    async with session.get(f"{API_URL}/orders/", headers=headers) as resp:
        return await resp.json()


async def cancel_order(session, token, order_id):
    """Cancel a single order"""
    headers = {'Authorization': f'Bearer {token}'}
    async with session.post(f"{API_URL}/orders/{order_id}/cancel", headers=headers) as resp:
        if resp.status == 200:
            print(f"✅ Cancelled order {order_id}")
            return True
        else:
            error = await resp.text()
            print(f"❌ Failed to cancel order {order_id}: {error}")
            return False


async def main():
    print("🧹 Cancelling all pending orders...\n")

    async with aiohttp.ClientSession() as session:
        # Login
        print("🔐 Logging in...")
        token = await login(session)
        print("✅ Logged in!\n")

        # Get all orders
        print("📦 Fetching orders...")
        orders = await get_orders(session, token)
        pending_orders = [o for o in orders if o['status'] == 'pending']
        print(f"Found {len(pending_orders)} pending orders\n")

        if not pending_orders:
            print("No pending orders to cancel!")
            return

        # Cancel them all
        print("🗑️  Cancelling orders...")
        tasks = [cancel_order(session, token, order['id']) for order in pending_orders]
        results = await asyncio.gather(*tasks)

        successful = sum(results)
        print(f"\n{'=' * 50}")
        print(f"📊 Cancelled {successful}/{len(pending_orders)} orders")
        print(f"{'=' * 50}")


if __name__ == "__main__":
    asyncio.run(main())