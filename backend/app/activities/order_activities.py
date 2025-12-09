import asyncio
import os
from datetime import datetime
from typing import List

import httpx
from temporalio import activity
import time

from temporalio.exceptions import ActivityError

import crud
from config import INVENTORY_API_URL
from database import SessionLocal
from models import Order
from schemas import OrderCreate, OrderItemCreate
from temporal_models import OrderFulfillmentInput, OrderFulfillmentResult

SLEEP_TIME=1

@activity.defn
async def create_order_activity(input: OrderFulfillmentInput) -> dict:
    """Activity: Create order in database"""
    activity.logger.info(f"Creating order with {len(input.items)} items")

    db = SessionLocal()
    try:
        order_items = [
            OrderItemCreate(
                product_id=item.product_id,
                quantity=item.quantity,
            )
            for item in input.items
        ]

        order_create = OrderCreate(items=order_items)
        order = await asyncio.to_thread(crud.create_order_db, db, order_create, input.user_id)

        return {
            "id": order.id,
            "status": order.status,
            "created_at": order.created_at.isoformat() if order.created_at else None
        }

    except Exception as e:
        activity.logger.error(f"Failed to create order: {e}")
        raise

    finally:
        db.close()

@activity.defn
async def get_order_activity(order_id: int) -> dict:
    """Activity: Get order details"""
    activity.logger.info(f"Fetching order {order_id}")
    db = SessionLocal()
    try:
        order = await asyncio.to_thread(crud.get_order, db, order_id)
        if not order:
            raise Exception(f"Order {order_id} not found")

        return {
            "id": order.id,
            "status": order.status,
            "owner_id": order.owner_id,
            "owner_email": order.owner.email,
            "created_at": order.created_at.isoformat(),
        }
    finally:
        db.close()

@activity.defn
async def update_order_status_activity(order_id: int, status: str):
    """Activity: Update order status"""
    activity.logger.info(f"Updating order {order_id} to status: {status}")
    db = SessionLocal()

    try:
        await asyncio.sleep(SLEEP_TIME)
        order = await asyncio.to_thread(crud.update_order_status, db, order_id, status)
        return {"id": order.id, "status": order.status}
    finally:
        db.close()

@activity.defn
async def check_inventory_activity(order_id: int) -> bool:
    """Activity: Check if inventory is available"""
    activity.logger.info(f"Checking inventory for order {order_id}")
    db = SessionLocal()

    try:
        await asyncio.sleep(SLEEP_TIME)
        return await asyncio.to_thread(crud.check_inventory, db, order_id)
    finally:
        db.close()

@activity.defn
async def reserve_inventory_activity(order: OrderFulfillmentInput) -> List[str]:
    reservation_ids = []
    async with httpx.AsyncClient() as client:
        try:
            for product in order.items:
                response = await client.post(
                    f"{INVENTORY_API_URL}/reserve",
                    json={
                        "orderId": f"order-{order.order_id}",
                        "productId": product.product_id,
                        "quantity": product.quantity,
                    }
                )
                if response.status_code == 201:
                    reservation_ids.append(response.json()["reservationId"])
                else:
                    raise ActivityError(
                        f"Insufficient inventory for product {product.product_id}: {response.json().get('message', response.text)}"
                    )

            return reservation_ids
        except Exception as e:
            raise ActivityError(f"Error reserving inventory: {e}")

@activity.defn
async def allocate_inventory_activity(order_id: int) -> dict:
    """Activity: Allocate inventory for order"""
    activity.logger.info(f"Allocating inventory for order {order_id}")
    db = SessionLocal()
    return_value: dict = {}

    try:
        await asyncio.sleep(1)
        result = await asyncio.to_thread(crud.allocate_inventory, db, order_id)

        # Return success with details
        return_value = {
            "success": True,
            "order_id": order_id,
            "allocated_items": result  # Assuming crud returns item details
        }

    except crud.InsufficientInventoryError as e:
        # Return error dict with full details
        return_value = {
            "success": False,
            "error": "insufficient_inventory",
            "product_name": e.product_name,
            "available": e.available,
            "requested": e.requested,
            "message": str(e)
        }

    except Exception as e:
        # Generic error
        return_value = {
            "success": False,
            "error": "allocation_failed",
            "message": str(e)
        }

    finally:
        db.close()

    return return_value

@activity.defn
async def notify_fulfillment_activity(order_id: int) -> dict:
    """Activity: Notify fulfillment team"""
    activity.logger.info(f"Notifying fulfillment for order {order_id}")
    result = await asyncio.to_thread(crud.notify_fulfillment, order_id)
    return {"status": "notified", "order_id": order_id, "result": result}

@activity.defn
async def send_confirmation_activity(order_id: int, customer_email: str) -> dict:
    """
    Mock function to send order confirmation email.
    In production, this would use SendGrid, AWS SES, etc.
    """
    activity.logger.info(f"[EMAIL] Sending confirmation for Order #{order_id} to {customer_email}")
    # TODO Send the email
    await asyncio.sleep(SLEEP_TIME)
    return {
        "status": "sent",
        "order_id": order_id,
        "email": customer_email,
        "timestamp": datetime.now().isoformat()
    }


async def validate_order_rules():
    return None