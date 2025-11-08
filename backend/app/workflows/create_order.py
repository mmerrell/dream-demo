import asyncio
from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from activities.order_activities import create_order_activity

DEFAULT_RETRY_POLICY = RetryPolicy(
    maximum_attempts=3,
    initial_interval=timedelta(seconds=1),
    maximum_interval=timedelta(seconds=10),
    backoff_coefficient=2.0,
)

@workflow.defn
class OrderProcessingWorkflow:

    def __init__(self):
        self.current_step = "Initializing"
        self.steps_completed = []
        self.is_paused = False

    @workflow.run
    async def create_order_workflow(self, order_data: dict, user_id: int) -> dict:
        workflow.logger.info(f"\n{'=' * 50}")
        workflow.logger.info(f"Creating order record for user: {user_id}, {len(order_data['items'])} items")
        workflow.logger.info(f"{'=' * 50}\n")

        try:
            self.current_step = ("Checking Inventory")
            await self._wait_if_paused()
            await asyncio.sleep(1) # TODO - remove sleep in favor of real microservice call

            self.current_step = ("Creating Order")
            await self._wait_if_paused()
            order_dict: dict = await workflow.execute_activity(
                create_order_activity,
                args=[order_data, user_id],
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=DEFAULT_RETRY_POLICY
            )

            workflow.logger.info(f"\n{'=' * 50}")
            workflow.logger.info(f"Order {order_dict['id']} created")
            workflow.logger.info(f"{'=' * 50}\n")

            self.current_step = ("Order Created")
            return order_dict

        except Exception as e:
            workflow.logger.info(f"\n❌ FAILURE: {str(e)}")
            workflow.logger.info("Manual intervention required - automatic retry failed!\n")
            raise e

    @workflow.query
    def get_status(self) -> dict:
        return {
            "current_step": self.current_step,
            "steps_completed": self.steps_completed,
            "current_step_number": len(self.steps_completed),
            "total_steps": 5,
        }

    @workflow.signal
    async def pause(self):
        self.is_paused = True
        workflow.logger.info("▶️  Workflow RESUMED")

    @workflow.signal
    async def resume(self):
        self.is_paused = False
        workflow.logger.info("⏸️  Workflow PAUSED")

    @workflow.query
    def is_paused_query(self) -> bool:
        return self.is_paused

    async def _wait_if_paused(self):
        await workflow.wait_condition(lambda: not self.is_paused)