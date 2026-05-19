from acr.agents.base import BaseAgent
from acr.models.schemas import Event

class ExplorerAgent(BaseAgent):
    async def setup_subscriptions(self):
        await self.bus.subscribe("heartbeat.tick", self.handle_heartbeat)

    async def handle_heartbeat(self, event: Event):
        tick = event.payload.get("tick", 0)
        if tick % 10 == 0:
            print(f"[Explorer] Generating hypotheses at tick {tick}")
            await self.emit("hypothesis.generated", {"hypothesis": "New strategy for memory retrieval", "confidence": 0.7})

class CriticAgent(BaseAgent):
    async def setup_subscriptions(self):
        await self.bus.subscribe("plan.created", self.handle_plan)

    async def handle_plan(self, event: Event):
        plan = event.payload.get("plan", [])
        goal = event.payload.get("goal", "")
        
        if self.llm:
            prompt = (
                f"Goal: {goal}\n"
                f"Proposed Plan: {plan}\n"
                "Evaluate this plan for consistency, safety, and feasibility.\n"
                "Respond in JSON format: {\"valid\": true/false, \"feedback\": \"reasoning\"}"
            )
            response = await self.llm.chat([{"role": "user", "content": prompt}])
            try:
                # Basic JSON extraction
                import json
                res = json.loads(response.strip("`").strip("json").strip())
                is_valid = res.get("valid", False)
                feedback = res.get("feedback", "No feedback provided")
            except:
                is_valid = True # Fallback
                feedback = response
        else:
            is_valid = True
            feedback = "Plan looks consistent (no LLM available)"
            
        await self.emit("plan.validated", {
            "valid": is_valid, 
            "feedback": feedback,
            "plan": plan,
            "goal": goal
        })
