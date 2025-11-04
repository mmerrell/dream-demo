from datetime import timedelta
from temporalio.common import RetryPolicy
from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from activities.order_activities import (
        get_order_activity,
        update_order_status_activity,
        check_inventory_activity,
        allocate_inventory_activity,
        notify_fulfillment_activity,
        send_confirmation_activity,
    )
    from crud import InsufficientInventoryError, InventoryAllocationFailedError


DEFAULT_RETRY_POLICY = RetryPolicy(
    maximum_attempts=3,
    initial_interval=timedelta(seconds=1),
    maximum_interval=timedelta(seconds=10),
    backoff_coefficient=2.0,
)

@workflow.defn
class ProcessPaymentWorkflow:
    """
        1. Update order status to 'paid'
        2. Check inventory availability
        3. Allocate inventory
        4. Notify fulfillment
        5. Send confirmation email
    """

    def __init__(self):
        self.current_step = "Initializing"
        self.steps_completed = []
        self.is_paused = False

    @workflow.run
    async def process_payment_workflow(self, order_id: int) -> dict:
        workflow.logger.info(f"\n{'=' * 50}")
        workflow.logger.info(f"Getting info for id: {order_id}")
        workflow.logger.info(f"{'=' * 50}\n")

        try:
            self.current_step = "Fetching order details"
            order = await workflow.execute_activity(
                get_order_activity,
                order_id,
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=DEFAULT_RETRY_POLICY,
            )

            # 1. Update order status to 'paid'
            self.current_step = "Payment processed"
            workflow.logger.info(f"Payment processed: {order_id}")
            await self._update_status(order_id, "paid")

            # 2. Check inventory availability
            self.current_step = "Checking inventory"
            workflow.logger.info(f"Checking inventory")
            check_inventory_result = await workflow.execute_activity(
                check_inventory_activity,
                args=[order_id],
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=DEFAULT_RETRY_POLICY,
            )
            if not check_inventory_result:
                await self._update_status(order_id, "insufficient_inventory")
                raise InsufficientInventoryError(f"There is insufficient inventory for order {order_id}")

            await self._update_status(order_id, "processing")
            workflow.logger.info(f"[WAREHOUSE] Order #{order_id} picked and being packed")

            # 3. Allocate inventory
            self.current_step = "Allocating inventory"
            workflow.logger.info(f"Allocating inventory")
            allocation_result = await workflow.execute_activity(
                allocate_inventory_activity,
                args=[order_id],
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=DEFAULT_RETRY_POLICY,
            )

            # Check if allocation failed
            if not allocation_result.get("success"):
                await self._update_status(order_id, "inventory_allocation_failed")

                error_type = allocation_result.get("error")

                if error_type == "insufficient_inventory":
                    # Detailed error
                    raise InsufficientInventoryError(
                        product_name=allocation_result["product_name"],
                        available=allocation_result["available"],
                        requested=allocation_result["requested"]
                    )
                else:
                    # Generic error
                    raise InventoryAllocationFailedError(
                        allocation_result.get("message", "Unknown allocation error")
                    )
            workflow.logger.info(f"Inventory allocated: {allocation_result['allocated_items']}")

            # 4. Notify fulfillment
            self.current_step = "Notify fulfillment"
            workflow.logger.info(f"Notify fulfillment")
            fulfillment_result = await workflow.execute_activity(
                notify_fulfillment_activity,
                args=[order_id],
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=DEFAULT_RETRY_POLICY,
            )

            # 5. Send confirmation email
            self.current_step = "Send confirmation email"
            workflow.logger.info(f"Send confirmation email")
            confirmation_result = await workflow.execute_activity(
                send_confirmation_activity,
                args=[order_id, order["owner_email"]],
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=DEFAULT_RETRY_POLICY,
            )

            await self._update_status(order_id, "completed")
            workflow.logger.info(f"[DELIVERY] Order #{order_id} delivered successfully")

            # TODO return Temporal-friendly object
            return {
                "status": "success",
                "order_id": order_id,
                "fulfillment": fulfillment_result,
                "confirmation": confirmation_result
            }

        except Exception as e:
            workflow.logger.info(f"\n❌ FAILURE: {str(e)}")
            workflow.logger.info("Manual intervention required - automatic retry failed!\n")
            raise e

    async def _update_status(self, order_id: int, status: str):
        """Helper: Update order status with standard timeouts"""
        await workflow.execute_activity(
            update_order_status_activity,
            args=[order_id, status],
            start_to_close_timeout=timedelta(seconds=10),
            retry_policy=DEFAULT_RETRY_POLICY,
        )
        workflow.logger.info(f"Order {order_id} status updated to: {status}")