import asyncio
from typing import Dict, Any, Optional
from acr.core.bus import EventBus
from acr.models.schemas import Event
from acr.core.llm import LLMClient

class BaseAgent:
    def __init__(self, name: str, bus: EventBus, llm: Optional[LLMClient] = None):
        self.name = name
        self.bus = bus
        self.llm = llm

    async def start(self):
        print(f"[Agent:{self.name}] Online.")
        await self.setup_subscriptions()
        
        # Start listening for subscribed events on Redis
        pubsub = self.bus.redis.pubsub()
        # We need to collect all channels this agent is interested in
        # This is a simplified version where agents listen to their subscriptions
        # In a real system, we'd use the EventBus.subscribe more effectively
        
        # For now, let's make sure the agent stays alive and can receive events
        while True:
            await asyncio.sleep(1)

    async def setup_subscriptions(self):
        """Override to subscribe to specific events."""
        pass

    async def emit(self, event_type: str, payload: Dict[str, Any], causal_id: Optional[str] = None):
        event = Event(
            event_type=event_type,
            source=self.name,
            payload=payload,
            causal_id=causal_id
        )
        await self.bus.publish(event)

    async def handle_event(self, event: Event):
        """Override to handle received events."""
        pass
