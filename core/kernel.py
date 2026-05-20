import asyncio
from typing import List, Any
from acr.core.bus import EventBus
from acr.core.runtime import HeartbeatRuntime
from acr.core.skills.manager import SkillManager
from acr.core.learning.learning import LearningManager
from acr.core.llm import LLMClient

class CognitiveKernel:
    def __init__(self, bus: EventBus, runtime: HeartbeatRuntime):
        self.bus = bus
        self.runtime = runtime
        self.agents: List[Any] = []
        
        # Internal Subsystems
        llm = LLMClient()
        self.skills = SkillManager()
        self.learning = LearningManager(bus, self.skills, llm)

    def register_agent(self, agent: Any):
        self.agents.append(agent)

    async def setup_internal_hooks(self):
        """Logic for autonomous learning."""
        async def on_execution_success(event):
            payload = event.payload if hasattr(event, 'payload') else event.get('payload', {})
            goal = payload.get("goal")
            if goal:
                await self.learning.analyze_success(goal, payload.get("steps", []), payload.get("results", []))

        await self.bus.subscribe("execution.completed", on_execution_success)

    async def boot(self):
        print("[Kernel] Orchestrating system boot...")
        await self.setup_internal_hooks()
        
        # Delegate execution loop to the Runtime
        await self.runtime.start(self.agents)

    def shutdown(self):
        print("[Kernel] Shutdown initiated.")
        self.runtime.stop()
