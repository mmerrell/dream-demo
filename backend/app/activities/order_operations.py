import asyncio
from datetime import datetime

from temporalio import activity
import time

import crud
from database import SessionLocal
from schemas import OrderCreate

@activity.defn
async def create_order_activity(order_data: dict, user_id: int) -> dict:
    """Activity: Create order in database"""
    activity.logger.info(f"Creating order with {len(order_data['items'])} items")

    db = SessionLocal()
    try:
        order_create = OrderCreate(**order_data)
        order = await asyncio.to_thread(crud.create_order_db, db, order_create, user_id)
        return {
            "id": order.id,
            "status": order.status,
            "owner_id": order.owner_id,
            "created_at": order.created_at.isoformat(),
            "items": [
                {
                    "id": item.id,
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "price_at_purchase": float(item.price_at_purchase),
                }
                for item in order.items
            ],
        }

    except crud.ProductNotFoundError as e:
        return {
            "error": "product_not_found",
            "message": str(e),
            "product_id": e.product_id
        }

    except crud.InsufficientInventoryError as e:
        return {
            "error": "insufficient_inventory",
            "message": str(e),
            "product": e.product_name
        }
    finally:
        db.close()

@activity.defn
async def process_order_payment(order_id: int) -> dict:
    """
    Complete payment processing workflow:
    1. Update order status to 'paid'
    2. Check inventory availability
    3. Allocate inventory
    4. Notify fulfillment
    5. Send confirmation email

    NOTE: This function simulates realistic delays between order states
    that would occur in a production environment.
    """
    db = SessionLocal()

    order = crud.get_order(db, order_id)
    if not order:
        # TODO return Temporal-friendly object
        return {"status": "error", "message": "Order not found"}

    # 3. Allocate inventory
    # TODO activity
    if not crud.allocate_inventory(db, order_id):
        await update_order_status_activity(db, order_id, "inventory_allocation_failed")
        # TODO return Temporal-friendly object
        return {
            "status": "error",
            "message": "Failed to allocate inventory",
            "order_id": order_id
        }

    # Update status to processing (order being prepared/packed)
    # TODO activity
    await update_order_status_activity(db, order_id,"processing")
    activity.logger.info(f"[WAREHOUSE] Order #{order_id} picked and being packed")

    # Simulate warehouse processing time (realistic: 5-10 seconds for demo, hours in reality)
    time.sleep(5)

    # 4. Notify fulfillment
    # TODO activity (this might actually be a workflow)
    fulfillment_result = crud.notify_fulfillment(order_id)
    activity.logger.info(f"[SHIPPING] Order #{order_id} shipped")

    # Simulate shipping/delivery time (realistic: 3 seconds for demo, days in reality)
    time.sleep(3)

    # Send confirmation email
    # TODO activity
    confirmation_result = await send_confirmation_activity(order_id, order.owner.email)

    # Mark as complete (delivered)
    # TODO activity
    await update_order_status_activity(db, order_id,"completed")
    activity.logger.info(f"[DELIVERY] Order #{order_id} delivered successfully")

    # TODO return Temporal-friendly object
    return {
        "status": "success",
        "order_id": order_id,
        "fulfillment": fulfillment_result,
        "confirmation": confirmation_result
    }

@activity.defn
async def update_order_status_activity(db, order_id, status):
    crud.update_order_status(db, order_id, status)

@activity.defn
async def check_inventory_activity(db, order_id) -> bool:
    return crud.check_inventory(db, order_id)

@activity.defn
async def allocate_inventory_activity(db, order_id) -> bool:
    return crud.allocate_inventory(db, order_id)

@activity.defn
async def notify_fulfillment_activity(db, order_id) -> dict:
    return crud.notify_fulfillment(order_id)

@activity.defn
async def send_confirmation_activity(order_id: int, customer_email: str) -> dict:
    """
    Mock function to send order confirmation email.
    In production, this would use SendGrid, AWS SES, etc.
    """
    activity.logger.info(f"[EMAIL] Sending confirmation for Order #{order_id} to {customer_email}")
    # TODO Send the email
    return {
        "status": "sent",
        "order_id": order_id,
        "email": customer_email,
        "timestamp": datetime.now().isoformat()
    }

