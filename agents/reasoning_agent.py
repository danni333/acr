from typing import Any, Optional
from acr.agents.base import BaseAgent
from acr.models.schemas import Event
from acr.memory.causal import CausalGraph

class ReasoningAgent(BaseAgent):
    """Analyzes causal relationships between experiences."""
    def __init__(self, name: str, bus: Any, causal_graph: CausalGraph, llm: Optional[Any] = None):
        super().__init__(name, bus, llm=llm)
        self.causal_graph = causal_graph

    async def setup_subscriptions(self):
        await self.bus.subscribe("anomaly.detected", self.analyze_anomaly)
        await self.bus.subscribe("system.heartbeat", self.periodic_reflection)

    async def analyze_anomaly(self, event: Event):
        anomaly_reason = event.payload.get("reason")
        print(f"[Reasoning] Analyzing anomaly: {anomaly_reason}")
        if self.llm:
            prompt = f"An anomaly was detected: {anomaly_reason}. Trace back potential causes."
            response = await self.llm.chat([{"role": "user", "content": prompt}])
            await self.emit("causal.hypothesis", {"hypothesis": response, "anomaly": anomaly_reason})

    async def periodic_reflection(self, event: Event):
        """Autonomous thinking triggered by heartbeat."""
        print(f"[Reasoning] Autonomous Thinking: Analyzing recent experiences...")
        if self.llm:
            # In a real system, we would fetch the last 10 episodic memories here
            prompt = (
                "Sei il motore di ragionamento di ACR. È passato un minuto di esecuzione.\n"
                "Rifletti sullo stato del sistema (sei online e pronto).\n"
                "Genera un breve pensiero interno (massimo 1 riga) su cosa potresti fare per aiutare l'utente oggi."
            )
            thought = await self.llm.chat([{"role": "system", "content": "Sei un'IA cognitiva persistente."}, {"role": "user", "content": prompt}])
            await self.emit("agent.response", {"content": f"[Riflessione Interna] {thought}"})
