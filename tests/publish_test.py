import redis
import json
from datetime import datetime
import os

host = os.getenv("REDIS_HOST", "localhost")
r = redis.Redis(host=host, port=6379, db=0)

event = {
    "event_type": "goal.update",
    "source": "user_cli",
    "payload": {"goal": "Analizzare l'efficienza del sistema ACR"},
    "timestamp": datetime.now().isoformat()
}

r.publish("goal.update", json.dumps(event))
print("Event published!")
