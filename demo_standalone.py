import asyncio
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

# --- PURE PYTHON SHIM (Mocks Pydantic & Redis) ---

class MockBaseModel:
    def __init__(self, **data):
        for k, v in data.items():
            setattr(self, k, v)
    def model_dump_json(self):
        import json
        return json.dumps(self.__dict__, default=str)

class Event(MockBaseModel):
    event_type: str
    source: str
    payload: Dict[str, Any]
    timestamp: datetime
    causal_id: Optional[str] = None

class MockBus:
    def __init__(self):
        self.subscribers = {}
    async def publish(self, event):
        print(f"  [BUS] >> {event.event_type} from {event.source}")
        if event.event_type in self.subscribers:
            for cb in self.subscribers[event.event_type]:
                asyncio.create_task(cb(event))
        if "*" in self.subscribers:
            for cb in self.subscribers["*"]:
                asyncio.create_task(cb(event))
    async def subscribe(self, etype, cb):
        if etype not in self.subscribers:
            self.subscribers[etype] = []
        self.subscribers[etype].append(cb)
    async def listen(self): pass

# --- CORE LOGIC (Simplified from ACR) ---

class Heartbeat:
    def __init__(self, bus):
        self.bus = bus
        self.tick = 0
    async def run(self):
        while self.tick < 5:
            self.tick += 1
            print(f"\n[HEARTBEAT] Tick {self.tick}")
            await self.bus.publish(Event(
                event_type="heartbeat.tick", source="kernel", 
                payload={"tick": self.tick}, timestamp=datetime.now()
            ))
            await asyncio.sleep(1)

class Agent:
    def __init__(self, name, bus):
        self.name = name
        self.bus = bus
    async def start(self):
        await self.bus.subscribe("heartbeat.tick", self.on_tick)
        await self.bus.subscribe("goal.update", self.on_goal)
    async def on_tick(self, ev):
        if ev.payload["tick"] % 2 == 0:
            print(f"  [{self.name}] Reasoning cycle triggered...")
    async def on_goal(self, ev):
        print(f"  [{self.name}] NEW GOAL: {ev.payload['goal']}")

async def run_demo():
    print("=== ACR COGNITIVE RUNTIME DEMO (Standalone Mode) ===")
    bus = MockBus()
    hb = Heartbeat(bus)
    planner = Agent("Planner", bus)
    memory = Agent("Memory", bus)
    
    await planner.start()
    await memory.start()
    
    # Simulate a user goal
    await asyncio.sleep(0.5)
    await bus.publish(Event(
        event_type="goal.update", source="user", 
        payload={"goal": "Implement self-awareness (simulation)"}, 
        timestamp=datetime.now()
    ))
    
    await hb.run()
    print("\n=== Demo Complete ===")

if __name__ == "__main__":
    asyncio.run(run_demo())
