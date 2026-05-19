import asyncio
import os

async def run(params=None):
    """A sample skill that returns system info."""
    load = os.getloadavg()
    return {
        "status": "success",
        "load_average": load,
        "message": f"ACR System load: {load[0]}, {load[1]}, {load[2]}"
    }
