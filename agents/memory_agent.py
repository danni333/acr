from typing import Any
from acr.agents.base import BaseAgent
from acr.models.schemas import Event
from acr.memory.manager import MemoryManager

class MemoryAgent(BaseAgent):
    def __init__(self, name: str, bus: Any, memory_manager: MemoryManager):
        super().__init__(name, bus)
        self.memory_manager = memory_manager

    async def setup_subscriptions(self):
        # Subscribe to everything to record episodic memory
        # In a real system, we might be more selective or use a dedicated logger
        await self.bus.subscribe("*", self.handle_any_event)
        await self.bus.subscribe("memory.retrieve", self.handle_retrieval)

    async def handle_any_event(self, event: Event):
        # Record all events as episodic memory
        if event.event_type != "heartbeat.tick": # Avoid flooding with ticks
            await self.memory_manager.store_episodic(event)

    async def handle_retrieval(self, event: Event):
        query = event.payload.get("query")
        results = await self.memory_manager.retrieve_semantic(query)
        await self.emit("memory.response", {"results": results}, causal_id=str(event.timestamp))
