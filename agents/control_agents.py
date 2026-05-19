from acr.agents.base import BaseAgent
from acr.models.schemas import Event

class PrefrontalAgent(BaseAgent):
    """Responsible for goal arbitration and long-term goal management."""
    async def setup_subscriptions(self):
        await self.bus.subscribe("goal.update", self.handle_goal)
        await self.bus.subscribe("heartbeat.tick", self.handle_tick)

    async def handle_goal(self, event: Event):
        goal = event.payload.get("goal")
        print(f"[Prefrontal] Arbitrating goal: {goal}")
        # Logic to prioritize goals
        await self.emit("goal.prioritized", {"goal": goal, "priority": 1})

    async def handle_tick(self, event: Event):
        tick = event.payload.get("tick", 0)
        if tick % 20 == 0:
            print(f"[Prefrontal] Reviewing long-term goals...")
            await self.emit("memory.retrieve", {"query": "long-term objectives"})

class AnomalyAgent(BaseAgent):
    """Detects inconsistencies and system stability issues."""
    async def setup_subscriptions(self):
        await self.bus.subscribe("*", self.check_anomaly)

    async def check_anomaly(self, event: Event):
        # Basic heuristic for anomaly detection
        if event.event_type == "execution.completed" and event.payload.get("status") == "failure":
            print(f"[Anomaly] Detection failure in event: {event.event_type}")
            await self.emit("anomaly.detected", {
                "reason": "action_failure",
                "source_event": event.event_type,
                "source_event_id": event.causal_id, # Link back to the parent that caused this
                "timestamp": str(event.timestamp)
            })
