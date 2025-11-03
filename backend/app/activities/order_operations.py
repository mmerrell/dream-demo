import asyncio

from temporalio import activity
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
    import time
    db = SessionLocal()

    order = crud.get_order(db, order_id)
    if not order:
        return {"status": "error", "message": "Order not found"}

    # Update order status to paid (payment confirmed)
    order = crud.update_order_status(db, order_id, "paid")
    print(f"[PAYMENT] Order #{order_id} payment confirmed - awaiting fulfillment")

    # Simulate payment settlement delay (realistic: 1-2 seconds)
    time.sleep(2)

    # Check inventory
    if not crud.check_inventory(db, order_id):
        crud.update_order_status(db, order_id, "payment_failed")
        return {
            "status": "error",
            "message": "Insufficient inventory",
            "order_id": order_id
        }

    # Allocate inventory
    if not crud.allocate_inventory(db, order_id):
        crud.update_order_status(db, order_id, "payment_failed")
        return {
            "status": "error",
            "message": "Failed to allocate inventory",
            "order_id": order_id
        }

    # Update status to processing (order being prepared/packed)
    crud.update_order_status(db, order_id, "processing")
    print(f"[WAREHOUSE] Order #{order_id} picked and being packed")

    # Simulate warehouse processing time (realistic: 5-10 seconds for demo, hours in reality)
    time.sleep(5)

    # Notify fulfillment team
    fulfillment_result = crud.notify_fulfillment(order_id)
    print(f"[SHIPPING] Order #{order_id} shipped")

    # Simulate shipping/delivery time (realistic: 3 seconds for demo, days in reality)
    time.sleep(3)

    # Send confirmation email
    confirmation_result = crud.send_confirmation(order_id, order.owner.email)

    # Mark as complete (delivered)
    crud.update_order_status(db, order_id, "completed")
    print(f"[DELIVERY] Order #{order_id} delivered successfully")

    return {
        "status": "success",
        "order_id": order_id,
        "fulfillment": fulfillment_result,
        "confirmation": confirmation_result
    }