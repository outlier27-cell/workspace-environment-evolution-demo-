from __future__ import annotations

from fastapi import FastAPI

from environment_agent.api import app as environment_agent_app


# Vercel's Python runtime discovers this ASGI app from /api/index.py.
# Local development can run the same object with:
#   python -m uvicorn api.index:app --reload --port 8765
app = FastAPI(title="Workspace-Bench Environment Agent API Demo")
app.mount("/api", environment_agent_app)
app.mount("/", environment_agent_app)
