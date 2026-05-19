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
        print(f"[Agent:{self.name}] Starting...")
        await self.setup_subscriptions()

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
