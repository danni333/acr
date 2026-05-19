import redis
import json
from datetime import datetime
import os

host = os.getenv("REDIS_HOST", "localhost")
r = redis.Redis(host=host, port=6379, db=0)

event = {
    "event_type": "goal.update",
    "source": "user_cli",
    "payload": {"goal": "Ricerca e riassumi le ultime tendenze nei Cognitive Agent Runtimes del 2025."},
    "timestamp": datetime.now().isoformat()
}

r.publish("goal.update", json.dumps(event))
print("Complex research goal published!")
