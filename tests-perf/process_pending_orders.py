# process_pending_orders.py
import asyncio
import aiohttp
from datetime import datetime

API_URL = "http://localhost:8000"
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
            raise Exception(f"Login failed: {error_text}")
        data = await resp.json()
        return data['access_token']


async def get_pending_orders(session, token):
    """Get all pending orders"""
    headers = {'Authorization': f'Bearer {token}'}
    async with session.get(f"{API_URL}/orders/", headers=headers) as resp:
        if resp.status != 200:
            raise Exception(f"Failed to get orders: {await resp.text()}")
        orders = await resp.json()
        return [o for o in orders if o['status'] == 'pending']


async def process_payment(session, token, order_id, order_num):
    """Trigger payment processing for an order"""
    headers = {'Authorization': f'Bearer {token}'}

    start_time = datetime.now()
    try:
        async with session.post(
                f"{API_URL}/orders/{order_id}/process-payment",
                headers=headers
        ) as resp:
            duration = (datetime.now() - start_time).total_seconds()

            if resp.status == 200:
                result = await resp.json()
                workflow_id = result.get('workflow_id', 'unknown')
                print(f"✅ Order {order_num} (ID: {order_id}): Workflow started - {workflow_id} - {duration:.2f}s")
                return {"success": True, "order_id": order_id, "workflow_id": workflow_id}
            else:
                error = await resp.text()
                print(f"❌ Order {order_num} (ID: {order_id}): Failed - {error} - {duration:.2f}s")
                return {"success": False, "order_id": order_id, "error": error}

    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        print(f"❌ Order {order_num} (ID: {order_id}): Exception - {e} - {duration:.2f}s")
        return {"success": False, "order_id": order_id, "error": str(e)}


async def main():
    print(f"{'=' * 60}")
    print(f"🚀 Processing All Pending Orders")
    print(f"{'=' * 60}\n")

    async with aiohttp.ClientSession() as session:
        # Login
        print("🔐 Logging in...")
        token = await login(session)
        print(f"✅ Logged in as {EMAIL}\n")

        # Get pending orders
        print("📦 Fetching pending orders...")
        pending_orders = await get_pending_orders(session, token)

        if not pending_orders:
            print("❌ No pending orders found!")
            return

        print(f"✅ Found {len(pending_orders)} pending orders\n")

        # Confirm
        print(f"⚠️  About to process {len(pending_orders)} orders concurrently!")
        print(f"   This will start {len(pending_orders)} Temporal workflows.")
        print(f"   Each workflow takes ~30-40 seconds with the current delays.\n")

        response = input("Continue? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("Cancelled.")
            return

        # Process all orders concurrently
        print(f"\n{'=' * 60}")
        print(f"🔥 Processing {len(pending_orders)} orders concurrently...")
        print(f"{'=' * 60}\n")

        start_time = datetime.now()

        tasks = [
            process_payment(session, token, order['id'], i + 1)
            for i, order in enumerate(pending_orders)
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        duration = (datetime.now() - start_time).total_seconds()

        # Summary
        successful = sum(1 for r in results if isinstance(r, dict) and r.get('success'))
        failed = len(results) - successful

        print(f"\n{'=' * 60}")
        print(f"📊 Results:")
        print(f"   Total orders: {len(pending_orders)}")
        print(f"   Workflows started: {successful}")
        print(f"   Failed to start: {failed}")
        print(f"   Total time: {duration:.2f}s")
        print(f"   Avg time per request: {duration / len(pending_orders):.2f}s")
        print(f"{'=' * 60}\n")

        print(f"🌐 Check Temporal UI: http://localhost:8080")
        print(f"📋 Watch worker logs: docker-compose logs -f payment-worker")
        print(f"\n⏳ Workflows will complete in ~30-40 seconds (with current activity delays)")


if __name__ == "__main__":
    asyncio.run(main())