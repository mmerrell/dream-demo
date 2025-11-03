from datetime import timedelta
from temporalio.common import RetryPolicy
from temporalio import workflow

from activities.order_operations import process_order_payment

DEFAULT_RETRY_POLICY = RetryPolicy(
    maximum_attempts=3,
    initial_interval=timedelta(seconds=1),
    maximum_interval=timedelta(seconds=10),
    backoff_coefficient=2.0,
)

@workflow.defn
class ProcessPaymentWorkflow:

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
            self.current_step = "Getting order info"
            workflow.logger.info(f"Getting info for order id: {order_id}")
            order_dict: dict = await workflow.execute_activity(
                process_order_payment,
                args=[order_id],
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=DEFAULT_RETRY_POLICY,
            )
            self.current_step = "Processing Payment"

        except Exception as e:
            workflow.logger.info(f"\n❌ FAILURE: {str(e)}")
            workflow.logger.info("Manual intervention required - automatic retry failed!\n")
            raise e

        return {}
