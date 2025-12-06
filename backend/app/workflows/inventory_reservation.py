import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone, time
from decimal import Decimal
from random import random
from typing import List, Optional

from temporalio import workflow
from temporalio.common import RetryPolicy

DEFAULT_RETRY_POLICY = RetryPolicy(
    maximum_attempts=3,
    initial_interval=timedelta(seconds=1),
    maximum_interval=timedelta(seconds=10),
    backoff_coefficient=2.0,
)

with workflow.unsafe.imports_passed_through:
    from activities.order_activities import (
        check_inventory_activity,
        allocate_inventory_activity,
        notify_fulfillment_activity,
        validate_order_rules,
    )

@dataclass
class ReservedItem:
    product_id: int
    quantity_reserved: int
    warehouse_location: str  # Where it's located
    expiration_time: datetime  # When reservation expires
    substitution_for: Optional[int] = None  # If substituted for different product
    lot_number: Optional[str] = None  # For perishables like flowers
    quality_grade: Optional[str] = None  # "Premium", "Standard"

@dataclass
class InventoryReservationResult:
    reservation_id: str
    reserved_items: List[ReservedItem]
    expires_at: datetime
    total_reserved_value: Decimal

@workflow.defn
class InventoryReservationWorkflow:

    def __init__(self, order_id: str):
        self.order_id = order_id

    @workflow.run
    async def run(self, order_id: str):
        # Step 1: Check availability
        await asyncio.sleep(4)
        await workflow.execute_activity(
            check_inventory_activity,
            args=[order_id],
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=DEFAULT_RETRY_POLICY,
        )

        # Step 2: Create soft reservations
        await asyncio.sleep(3)  # "Update inventory"
        await workflow.execute_activity(
            allocate_inventory_activity,
            args=[order_id],
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=DEFAULT_RETRY_POLICY,
        )

        # Step 3: Business rule validation
        await asyncio.sleep(2)  # "Rule engine check"
        await workflow.execute_activity(
            validate_order_rules,
            args=[order_id],
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=DEFAULT_RETRY_POLICY,
        )

        await asyncio.sleep(2)  # "Rule engine check"
        await workflow.execute_activity(
            notify_fulfillment_activity,
            args=[order_id],
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=DEFAULT_RETRY_POLICY,
        )

        # Step 4: Handle any conflicts (simulate occasional failure)
        # TODO these should be built into the activities, not in the workflow -- this isn't idempotent
        if random() < 0.05:  # 5% conflict rate
            raise InventoryConflictError("Stock was reserved by another order")

        # Step 5: Confirm reservation
        await asyncio.sleep(0.2)  # "Lock reservation"

        return InventoryReservationResult(
            reservation_id=f"res_{order_id}_{int(time.time())}",
            reserved_items=[
                ReservedItem(
                    product_id=item.product_id,
                    quantity_reserved=item.quantity,
                    warehouse_location=f"Section-A-{item.product_id}",
                    expiration_time=datetime.now() + timedelta(minutes=15)
                )
                for item in items
            ],
            expires_at=datetime.now() + timedelta(minutes=15),
            total_reserved_value=sum(item.price * item.quantity for item in items)
        )

class InventoryConflictError(Exception):
    """Raised when inventory reservation conflicts with another process"""
    def __init__(self, message: str, conflicted_items: List[int] = None, retry_after_seconds: int = None):
        self.message = message
        self.conflicted_items = conflicted_items or []
        self.retry_after_seconds = retry_after_seconds
        super().__init__(self.message)

class InventoryUnavailableError(Exception):
    """Raised when requested inventory is not available"""
    def __init__(self, message: str, unavailable_items: List[int] = None, available_quantity: int = 0):
        self.message = message
        self.unavailable_items = unavailable_items or []
        self.available_quantity = available_quantity
        super().__init__(self.message)

