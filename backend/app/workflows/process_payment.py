from datetime import timedelta
from temporalio.common import RetryPolicy
from temporalio import workflow

from activities.order_operations import update_order_status_activity, check_inventory_activity, allocate_inventory_activity, notify_fulfillment_activity, send_confirmation_activity
from crud import InsufficientInventoryError, ProductNotFoundError, InventoryAllocationFailedError
from main import update_order_status

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
            # 1. Update order status to 'paid'
            self.current_step = "Payment processed"
            workflow.logger.info(f"Payment processed: {order_id}")
            order_dict: dict = await workflow.execute_activity(
                update_order_status_activity,
                args=[order_id, "paid"],
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=DEFAULT_RETRY_POLICY,
            )

            # 2. Check inventory availability
            self.current_step = "Checking inventory"
            workflow.logger.info(f"Checking inventory: {order_dict['status']} for {len(order_dict['items'])} items")
            check_inventory_result = await workflow.execute_activity(
                check_inventory_activity,
                args=[order_id],
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=DEFAULT_RETRY_POLICY,
            )
            if not check_inventory_result:
                await workflow.execute_activity(
                    update_order_status_activity,
                    args=[order_id, "insufficient_inventory"],
                    start_to_close_timeout=timedelta(minutes=5),
                    retry_policy=DEFAULT_RETRY_POLICY,
                )
                raise InsufficientInventoryError(f"Failed to allocate inventory for order {order_id}")

            # 3. Allocate inventory
            self.current_step = "Allocating inventory"
            workflow.logger.info(f"Allocating inventory: {order_dict['status']} for {len(order_dict['items'])} items")
            allocate_inventory_result = await workflow.execute_activity(
                allocate_inventory_activity,
                args=[order_id],
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=DEFAULT_RETRY_POLICY,
            )
            if not allocate_inventory_result:
                await workflow.execute_activity(
                    update_order_status_activity,
                    args=[order_id, "inventory_allocation_failed"],
                )
                raise InventoryAllocationFailedError(f"Failed to allocate inventory for order {order_id}")

            # 4. Notify fulfillment
            self.current_step = "Notify fulfillment"
            workflow.logger.info(f"Notify fulfillment: {order_dict['status']}")
            await workflow.execute_activity(
                notify_fulfillment_activity,
                args=[order_id],
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=DEFAULT_RETRY_POLICY,
            )

            # 5. Send confirmation email
            self.current_step = "Send confirmation email"
            workflow.logger.info(f"Send confirmation email: {order_dict['status']}")
            await workflow.execute_activity(
                send_confirmation_activity,
                args=[order_id, "mmerrell@gmail.com"],
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=DEFAULT_RETRY_POLICY,
            )

        except Exception as e:
            workflow.logger.info(f"\n❌ FAILURE: {str(e)}")
            workflow.logger.info("Manual intervention required - automatic retry failed!\n")
            raise e

        return {}
