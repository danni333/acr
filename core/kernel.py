import asyncio
import json
from datetime import datetime
from typing import List, Any
from acr.core.bus import EventBus
from acr.core.runtime import HeartbeatRuntime

from acr.core.skills.manager import SkillManager
from acr.core.cron.scheduler import CognitiveScheduler
from acr.core.learning.learning import LearningManager
from acr.core.memory.vector_store import SemanticVectorStore

class CognitiveKernel:
    def __init__(self, bus: EventBus, runtime: HeartbeatRuntime):
        self.bus = bus
        self.runtime = runtime
        self.agents: List[Any] = []
        self.is_running = True
        
        # Core Cognitive Assets
        self.self_model = {
            "identity_summary": "ACR Autobiographical System v1.0",
            "active_goals": [],
            "memory_health": "100%",
            "contradiction_graph": {},
            "confidence_metrics": 0.95,
            "behavioral_trends": [],
            "system_stability": "STABLE"
        }
        
        # New Systems
        llm = LLMClient()
        self.skills = SkillManager()
        self.scheduler = CognitiveScheduler(bus)
        self.learning = LearningManager(bus, self.skills, llm)
        self.semantic_memory = SemanticVectorStore()
        
        self.scheduler.load_defaults()

    def register_agent(self, agent: Any):
        self.agents.append(agent)

    async def setup_internal_hooks(self):
        """Internal kernel logic for learning and automation."""
        async def on_execution_success(event):
            payload = event.get("payload", {})
            goal = payload.get("goal")
            steps = payload.get("steps", [])
            results = payload.get("results", [])
            if goal and steps:
                await self.learning.analyze_success(goal, steps, results)

        await self.bus.subscribe("execution.completed", on_execution_success)

    async def heartbeat_loop(self):
        """Continuous heartbeat to trigger autonomous agent reflections and Cron jobs."""
        print("[Kernel] Heartbeat loop active (60s pulse)")
        while self.is_running:
            await asyncio.sleep(60)
            heartbeat_event = {
                "event_type": "system.heartbeat",
                "source": "kernel",
                "payload": {"timestamp": datetime.now().isoformat()},
                "timestamp": datetime.now().isoformat()
            }
            await self.bus.publish("system.heartbeat", heartbeat_event)
            # Update and Persist Self-Model
            self.self_model["last_heartbeat"] = datetime.now().isoformat()
            with open("/home/tob/acr/workspace/self_model.json", "w") as f:
                json.dump(self.self_model, f, indent=2)
            
            # Trigger Scheduler
            await self.scheduler.handle_heartbeat(heartbeat_event)

    async def boot(self):
        print("[Kernel] Booting cognitive system...")
        # Setup internal automation
        await self.setup_internal_hooks()
        
        # Start agents
        agent_tasks = [asyncio.create_task(agent.run()) for agent in self.agents]
        
        # Start heartbeat
        heartbeat_task = asyncio.create_task(self.heartbeat_loop())
        
        # Start runtime
        await self.runtime.start()
        
        print("[Kernel] System ONLINE.")
        await asyncio.gather(*agent_tasks, heartbeat_task)

    def shutdown(self):
        print("[Kernel] Shutting down...")
        self.is_running = False
        self.runtime.stop()
