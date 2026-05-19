from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class SelfModel(BaseModel):
    identity_summary: str = "Autobiographical Cognitive Runtime (ACR) v0.1"
    active_goals: List[str] = []
    memory_health: float = 1.0
    contradiction_graph: Dict[str, Any] = {}
    confidence_metrics: Dict[str, float] = {}
    behavioral_trends: List[str] = []
    system_stability: float = 1.0
    last_updated: datetime = Field(default_factory=datetime.now)

class Event(BaseModel):
    event_type: str
    source: str
    payload: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)
    causal_id: Optional[str] = None  # Link to parent event
