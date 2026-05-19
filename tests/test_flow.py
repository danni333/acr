import asyncio
from acr.core.bus import EventBus
from acr.core.runtime import HeartbeatRuntime
from acr.agents.planner import PlannerAgent
from acr.tests.mock_redis import MockRedis
from acr.models.schemas import Event

async def test_acr_flow():
    print("Testing ACR Flow with Mock Redis...")
    bus = EventBus()
    # Patch bus with MockRedis
    bus.redis = MockRedis()
    bus.pubsub = bus.redis
    
    runtime = HeartbeatRuntime(bus, tick_interval=0.1)
    planner = PlannerAgent("test_planner", bus)
    
    await planner.start()
    
    # Manually publish a goal
    await bus.publish(Event(
        event_type="goal.update",
        source="tester",
        payload={"goal": "Design a cognitive system"}
    ))
    
    # Run a few ticks
    task = asyncio.create_task(runtime.start())
    await asyncio.sleep(0.5)
    runtime.stop()
    await task
    print("Test completed.")

if __name__ == "__main__":
    asyncio.run(test_acr_flow())
