from acr.agents.base import BaseAgent
from acr.models.schemas import Event

class PlannerAgent(BaseAgent):
    async def setup_subscriptions(self):
        await self.bus.subscribe("goal.update", self.handle_event)
        await self.bus.subscribe("heartbeat.tick", self.handle_heartbeat)

    async def handle_heartbeat(self, event: Event):
        # Every 5 ticks, review goals
        tick = event.payload.get("tick", 0)
        if tick % 5 == 0:
            print(f"[Planner] Reviewing goals at tick {tick}")
            await self.emit("memory.retrieve", {"query": "current active goals"})

    async def handle_event(self, event: Event):
        if event.event_type == "goal.update":
            goal = event.payload.get("goal")
            print(f"[Planner] New goal received: {goal}")
            
            if self.llm:
                prompt = f"Decompose the following goal into a list of actionable steps for a cognitive agent:\nGoal: {goal}\nRespond with only the list of steps."
                response = await self.llm.chat([{"role": "user", "content": prompt}])
                plan = [s.strip() for s in response.split("\n") if s.strip()]
            else:
                plan = ["step1", "step2"]
                
            await self.emit("plan.created", {"plan": plan, "goal": goal})
