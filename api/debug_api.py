from fastapi import FastAPI
from acr.models.schemas import SelfModel
from acr.core.bus import EventBus
import uvicorn

app = FastAPI(title="ACR Debug Interface")

# This would be injected or shared with the runtime
bus = EventBus()
self_model = SelfModel()

@app.get("/")
async def root():
    return {"status": "ACR Online", "self_model": self_model}

@app.get("/memory/health")
async def memory_health():
    return {"health": self_model.memory_health}

@app.post("/goal")
async def set_goal(goal: str):
    await bus.publish({
        "event_type": "goal.update",
        "source": "api",
        "payload": {"goal": goal}
    })
    return {"status": "Goal updated"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
