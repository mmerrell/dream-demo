import httpx
import os
from typing import Optional

INVENTORY_API_URL = os.getenv("INVENTORY_API_URL", "http://localhost:8001")

async def reserve_inventory(order_id: int, product_id: int, quantity: int) -> Optional[str]:
    """
    Reserve inventory for an order item.
    Returns reservation_id if successful, None if failed.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{INVENTORY_API_URL}/reserve",
                json={
                    "orderId": f"order-{order_id}",
                    "productId": product_id,
                    "quantity": quantity
                }
            )
            if response.status_code == 201:
                return response.json()["reservationId"]
            return None
        except Exception as e:
            print(f"Error reserving inventory: {e}")
            return None

async def commit_inventory(reservation_id: str) -> bool:
    """Commit a reservation after payment succeeds."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{INVENTORY_API_URL}/reserve/commit",
                json={"reservationId": reservation_id}
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error committing inventory: {e}")
            return False

async def rollback_inventory(reservation_id: str) -> bool:
    """Rollback a reservation if payment fails or order is cancelled."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{INVENTORY_API_URL}/reserve/rollback",
                json={"reservationId": reservation_id}
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error rolling back inventory: {e}")
            return False