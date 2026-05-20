import asyncio
import signal
import sys
import os
from datetime import datetime
from acr.core.bus import EventBus
from acr.core.runtime import HeartbeatRuntime
from acr.memory.manager import MemoryManager
from acr.agents.planner import PlannerAgent
from acr.agents.memory_agent import MemoryAgent
from acr.agents.research_agents import ExplorerAgent, CriticAgent
from acr.agents.executor import ExecutorAgent
from acr.agents.control_agents import PrefrontalAgent, AnomalyAgent
from acr.agents.reasoning_agent import ReasoningAgent

from acr.core.kernel import CognitiveKernel
from acr.core.llm import LLMClient

async def main():
    # Initialize Core
    bus = EventBus()
    memory_manager = MemoryManager()
    runtime = HeartbeatRuntime(bus, tick_interval=15.0)
    llm = LLMClient() 
    kernel = CognitiveKernel(bus, runtime)

    # Initialize Agents
    planner = PlannerAgent("planner", bus, llm=llm)
    memory_agent = MemoryAgent("memory_coordinator", bus, memory_manager)
    explorer = ExplorerAgent("explorer", bus, llm=llm)
    critic = CriticAgent("critic", bus, llm=llm)
    executor = ExecutorAgent("executor", bus, llm=llm)
    prefrontal = PrefrontalAgent("prefrontal_cortex", bus, llm=llm)
    anomaly = AnomalyAgent("anomaly_detector", bus)
    reasoning = ReasoningAgent("reasoning_engine", bus, memory_manager.causal_graph, llm=llm)

    # Register Agents with Kernel
    kernel.register_agent(planner)
    kernel.register_agent(memory_agent)
    kernel.register_agent(explorer)
    kernel.register_agent(critic)
    kernel.register_agent(executor)
    kernel.register_agent(prefrontal)
    kernel.register_agent(anomaly)
    kernel.register_agent(reasoning)

    # Boot Kernel
    try:
        await kernel.boot()
    except asyncio.CancelledError:
        pass
    except KeyboardInterrupt:
        pass
    finally:
        kernel.shutdown()
        print("[Main] ACR System shutting down...")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
