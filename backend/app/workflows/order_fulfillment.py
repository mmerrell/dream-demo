from datetime import timedelta
from enum import Enum

from temporalio import workflow
from temporalio.common import RetryPolicy


class OrderStatus(str, Enum):
    INITIALIZING = "initializing"
    CREATED = "created"
    INVENTORY_RESERVED = "inventory_reserved"
    PAYMENT_PROCESSING = "payment_processing"
    PAYMENT_CONFIRMED = "payment_confirmed"
    PACKAGING = "packaging"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    FAILED = "failed"

# In your order_fulfillment.py
from dataclasses import dataclass
from typing import List, Optional
from decimal import Decimal

@dataclass
class TemporalOrderItem:
    product_id: int
    quantity: int
    price: Decimal

@dataclass
class OrderFulfillmentInput:
    order_id: str
    customer_id: str
    items: List[TemporalOrderItem]  # Reuse existing model
    shipping_address: dict
    payment_method_id: str
    total_amount: Decimal

@dataclass
class OrderFulfillmentResult:
    order_id: str
    final_status: OrderStatus
    tracking_number: Optional[str] = None
    estimated_delivery: Optional[str] = None
    failure_reason: Optional[str] = None

with workflow.unsafe.imports_passed_through():
    from activities.order_activities import (
        update_order_status_activity,
        create_order_activity,
    )

DEFAULT_RETRY_POLICY = RetryPolicy(
    maximum_attempts=3,
    initial_interval=timedelta(seconds=1),
    maximum_interval=timedelta(seconds=10),
    backoff_coefficient=2.0,
)

@workflow.defn
class OrderFulfillmentWorkflow:

    def __init__(self):
        self.current_order_status: OrderStatus = OrderStatus.INITIALIZING
        self.steps_completed = []
        self.is_paused = False

    @workflow.run
    async def order_fulfillment(self, user_id: str, input: OrderFulfillmentInput) -> OrderFulfillmentResult:
        workflow.logger.info(f"\n{'=' * 50}")
        workflow.logger.info(f"Initializing order for user: {user_id}, {len(input.items)} items")
        workflow.logger.info(f"{'=' * 50}\n")

        await workflow.execute_activity(
            update_order_status_activity,
            args=[input.order_id, self.current_order_status],
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=DEFAULT_RETRY_POLICY,
        )

        try:
            # Step 1: Reserve Inventory

            inventory_result = await workflow.execute_child_workflow(
                OrderFulfillmentWorkflow.order_fulfillment,
                args=[input.order_id, self.current_order_status],
                id=f"inventory-{input.order_id}"
            )

            # Step 2: Process Payment (your existing workflow)
            # Step 3: Package Order
            # Step 4: Ship Order
            # Step 5: Delivery Confirmation

            return OrderFulfillmentResult(
                order_id=input.order_id,
                final_status=OrderStatus.DELIVERED,
                # tracking_number=shipping_result.tracking_number,
                # estimated_delivery=delivery_result.estimated_delivery
            )

        except Exception:
            await self.compensate_order(input.order_id, str(e))
            return OrderFulfillmentResult(
                order_id=input.order_id,
                final_status=OrderStatus.FAILED,
                failure_reason=str(e)
            )

    async def compensate_order(self, order_id: str, reason: str):
        """Handle order failures with compensation"""
        # Release inventory, refund payment, etc.
        pass

