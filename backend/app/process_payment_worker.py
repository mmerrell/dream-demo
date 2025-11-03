import asyncio
import sys

from temporalio.client import Client
from activities.order_activities import (
    get_order_activity,
    notify_fulfillment_activity,
    check_inventory_activity,
    allocate_inventory_activity,
    send_confirmation_activity,
    update_order_status_activity,
)

from temporalio.worker import Worker

from workflows.process_payment import ProcessPaymentWorkflow

async def main():
    print("🔧 Starting worker initialization...", flush=True)

    try:
        print("📡 Connecting to Temporal at temporal:7233...", flush=True)
        temporal_client = await Client.connect("temporal:7233")
        print("✅ Connected to Temporal!", flush=True)

        print("👷 Creating worker...", flush=True)
        worker = Worker(
            temporal_client,
            task_queue="process-payment-tasks",
            workflows=[ProcessPaymentWorkflow],
            activities=[
                get_order_activity,
                update_order_status_activity,
                send_confirmation_activity,
                notify_fulfillment_activity,
                allocate_inventory_activity,
                check_inventory_activity,
            ],
        )
    except Exception as e:
        print(f"❌ ERROR: {e}", file=sys.stderr, flush=True)
        raise

    print("🚀 Worker started - listening on task queue: process-payment-tasks", flush=True)
    print("Worker is now running and waiting for tasks...", flush=True)
    await worker.run()

if __name__ == "__main__":
    print("Starting process_order_worker.py...", flush=True)
    asyncio.run(main())
