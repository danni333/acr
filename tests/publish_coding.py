import redis
import json
from datetime import datetime
import os

host = os.getenv("REDIS_HOST", "localhost")
r = redis.Redis(host=host, port=6379, db=0)

event = {
    "event_type": "goal.update",
    "source": "user_cli",
    "payload": {"goal": "Crea uno script Python in 'hello.py' che stampi 'Hello from ACR' e poi eseguilo."},
    "timestamp": datetime.now().isoformat()
}

r.publish("goal.update", json.dumps(event))
print("Coding goal published!")
