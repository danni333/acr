import redis
import json
from datetime import datetime
import os

host = os.getenv("REDIS_HOST", "localhost")
r = redis.Redis(host=host, port=6379, db=0)

# Simulate a failed execution to trigger anomaly detection
event = {
    "event_type": "execution.completed",
    "source": "executor",
    "payload": {"status": "failure", "action": "web_search"},
    "timestamp": datetime.now().isoformat(),
    "causal_id": "parent_plan_id_123"
}

r.publish("execution.completed", json.dumps(event))
print("Simulated anomaly published!")
