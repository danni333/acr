import redis
import json
import asyncio
from typing import Callable, Any, Dict, List
from acr.models.schemas import Event

import os

class EventBus:
    def __init__(self, host=None, port=6379, db=0):
        if host is None:
            host = os.getenv("REDIS_HOST", "localhost")
        self.redis = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.pubsub = self.redis.pubsub()
        self._listeners: Dict[str, List[Callable]] = {}

    async def publish(self, event: Event):
        print(f"[EventBus] Publishing {event.event_type} from {event.source}")
        self.redis.publish(event.event_type, event.model_dump_json())

    async def subscribe(self, event_type: str, callback: Callable[[Event], Any]):
        if event_type not in self._listeners:
            self._listeners[event_type] = []
            if event_type == "*":
                self.pubsub.psubscribe(**{"*": self._handle_pmessage})
            else:
                self.pubsub.subscribe(**{event_type: self._handle_message})
        self._listeners[event_type].append(callback)

    def _handle_pmessage(self, message):
        if message['type'] == 'pmessage':
            data = json.loads(message['data'])
            event = Event(**data)
            for callback in self._listeners.get("*", []):
                asyncio.create_task(callback(event))

    def _handle_message(self, message):
        if message['type'] == 'message':
            data = json.loads(message['data'])
            event = Event(**data)
            for callback in self._listeners.get(event.event_type, []):
                asyncio.create_task(callback(event))

    async def listen(self):
        """Loop to listen for messages in a background thread or task."""
        while True:
            message = self.pubsub.get_message(ignore_subscribe_messages=True)
            if message:
                self._handle_message(message)
            await asyncio.sleep(0.01)
