import asyncio
import time
from typing import List, Dict, Any
from acr.core.bus import EventBus
from acr.models.schemas import Event, SelfModel
from acr.core.monitor import SystemMonitor

class HeartbeatRuntime:
    def __init__(self, bus: EventBus, tick_interval: float = 5.0):
        self.bus = bus
        self.tick_interval = tick_interval
        self.is_running = False
        self.self_model = SelfModel()
        self.monitor = SystemMonitor()
        self.tick_count = 0

    async def start(self):
        self.is_running = True
        print(f"[Runtime] Starting heartbeat loop with interval {self.tick_interval}s")
        asyncio.create_task(self.bus.listen())
        
        while self.is_running:
            start_time = time.time()
            self.tick_count += 1
            await self._tick()
            
            elapsed = time.time() - start_time
            sleep_time = max(0, self.tick_interval - elapsed)
            await asyncio.sleep(sleep_time)

    async def _tick(self):
        print(f"[Runtime] Tick {self.tick_count} start")
        
        # 1. Update Self-Model (collect stats, etc.)
        from datetime import datetime
        self.self_model = self.monitor.update_metrics(self.self_model)
        self.self_model.last_updated = datetime.now()
        
        # 2. Publish Heartbeat Event
        await self.bus.publish(Event(
            event_type="heartbeat.tick",
            source="runtime",
            payload={"tick": self.tick_count, "timestamp": datetime.now().isoformat()}
        ))
        
        # 3. Consolidation cycle (periodic)
        if self.tick_count % 10 == 0:
            await self._consolidate_memory()

    async def _consolidate_memory(self):
        print("[Runtime] Periodic memory consolidation...")
        await self.bus.publish(Event(
            event_type="memory.consolidate",
            source="runtime",
            payload={"reason": "periodic_maintenance"}
        ))

    def stop(self):
        self.is_running = False
