import asyncio
import json
from datetime import datetime
from typing import List, Dict, Any

class CognitiveScheduler:
    """Manages scheduled tasks (Cron) based on the cognitive heartbeat."""
    def __init__(self, bus):
        self.bus = bus
        self.jobs: List[Dict[str, Any]] = []

    def add_job(self, name: str, interval_heartbeats: int, event_type: str, payload: Dict[str, Any]):
        """Adds a job to be triggered every X heartbeats."""
        self.jobs.append({
            "name": name,
            "interval": interval_heartbeats,
            "event_type": event_type,
            "payload": payload,
            "counter": 0
        })

    async def handle_heartbeat(self, event):
        """Processes scheduled jobs on each heartbeat."""
        for job in self.jobs:
            job["counter"] += 1
            if job["counter"] >= job["interval"]:
                job["counter"] = 0
                print(f"[Scheduler] Triggering Cron Job: {job['name']}")
                trigger_event = {
                    "event_type": job["event_type"],
                    "source": "scheduler",
                    "payload": job["payload"],
                    "timestamp": datetime.now().isoformat()
                }
                await self.bus.publish(job["event_type"], trigger_event)

    def load_defaults(self):
        """Default ACR maintenance tasks."""
        self.add_job(
            name="Memory Consolidation",
            interval_heartbeats=10, # Every 10 mins approx
            event_type="memory.consolidate",
            payload={"action": "compress_episodes"}
        )
        self.add_job(
            name="Self-Health Check",
            interval_heartbeats=5,
            event_type="system.check",
            payload={"deep": True}
        )
