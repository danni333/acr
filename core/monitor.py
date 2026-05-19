import time
from typing import Dict, Any
from acr.models.schemas import SelfModel

class SystemMonitor:
    def __init__(self):
        self.start_time = time.time()
        self.event_counts = {}
        self.last_tick = time.time()

    def update_metrics(self, current_model: SelfModel) -> SelfModel:
        # Update system stability based on tick frequency
        now = time.time()
        tick_delta = now - self.last_tick
        self.last_tick = now
        
        # Stability decays if ticks are slow
        if tick_delta > 10.0:
            current_model.system_stability *= 0.95
        else:
            current_model.system_stability = min(1.0, current_model.system_stability * 1.01)
            
        # Update uptime in identity_summary or a separate field
        uptime = int(now - self.start_time)
        current_model.behavioral_trends.append(f"Uptime: {uptime}s")
        if len(current_model.behavioral_trends) > 10:
            current_model.behavioral_trends.pop(0)
            
        return current_model

    def record_event(self, event_type: str):
        self.event_counts[event_type] = self.event_counts.get(event_type, 0) + 1
