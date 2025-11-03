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