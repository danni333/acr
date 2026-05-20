import asyncio
import time
import json
import os
from datetime import datetime
from typing import List, Dict, Any
from acr.core.bus import EventBus
from acr.models.schemas import Event, SelfModel
from acr.core.monitor import SystemMonitor

class HeartbeatRuntime:
    def __init__(self, bus: EventBus, tick_interval: float = 60.0):
        self.bus = bus
        self.tick_interval = tick_interval
        self.is_running = False
        self.self_model_data = {
            "identity_summary": "ACR Autobiographical System v1.0",
            "start_time": datetime.now().isoformat(),
            "active_goals": [],
            "memory_health": "100%",
            "system_stability": "STABLE"
        }
        self.tick_count = 0

    async def start(self, agents: List[Any]):
        self.is_running = True
        print(f"[Runtime] System Pulse Active ({self.tick_interval}s)")
        
        # Start Bus Listener
        asyncio.create_task(self.bus.listen())
        
        # Start Agents
        for agent in agents:
            asyncio.create_task(agent.start())
        
        # Main Heartbeat Loop
        while self.is_running:
            start_time = time.time()
            self.tick_count += 1
            await self._tick()
            
            elapsed = time.time() - start_time
            sleep_time = max(0, self.tick_interval - elapsed)
            await asyncio.sleep(sleep_time)

    async def _tick(self):
        print(f"[Runtime] Tick {self.tick_count} | Processing cognitive cycle...")
        
        # 1. Update & Persist Self-Model
        self.self_model_data["last_heartbeat"] = datetime.now().isoformat()
        self.self_model_data["tick"] = self.tick_count
        
        try:
            path = "/home/tob/acr/workspace/self_model.json"
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                json.dump(self.self_model_data, f, indent=2)
        except Exception as e:
            print(f"[Runtime] Error saving self-model: {e}")

        # 2. Publish Heartbeat Event
        heartbeat_event = Event(
            event_type="system.heartbeat",
            source="runtime",
            payload={"tick": self.tick_count, "timestamp": datetime.now().isoformat()}
        )
        await self.bus.publish(heartbeat_event)

    def stop(self):
        self.is_running = False
