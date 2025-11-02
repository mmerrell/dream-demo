import asyncio
from temporalio.client import Client
from activities import create_order_activity
from temporalio.worker import Worker

from workflow import OrderProcessingWorkflow

async def main():
    print("🔧 Starting worker initialization...", flush=True)

    try:
        print("📡 Connecting to Temporal at temporal:7233...", flush=True)
        temporal_client = await Client.connect("temporal:7233")
        print("✅ Connected to Temporal!", flush=True)

        print("👷 Creating worker...", flush=True)
        worker = Worker(
            temporal_client,
            task_queue="create-order-tasks",
            workflows=[OrderProcessingWorkflow],
            activities=[create_order_activity],
        )
    except Exception as e:
        print(f"❌ ERROR: {e}", file=sys.stderr, flush=True)
        raise


    print("🚀 Worker started - listening on task queue: create-order-tasks", flush=True)
    print("Worker is now running and waiting for tasks...", flush=True)
    await worker.run()

if __name__ == "__main__":
    print("Starting worker.py...", flush=True)
    asyncio.run(main())
