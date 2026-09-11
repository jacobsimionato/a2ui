# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""FastAPI backend application for VitalCraft."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from agent import VitalCraftAgent
from database import get_recent_bp_readings, get_recent_exercises, get_vitals_summary

app = FastAPI(title="VitalCraft Health Assistant API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = VitalCraftAgent()


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Dict[str, str]]] = None


@app.get("/api/status")
async def get_status() -> Dict[str, Any]:
    """Returns local model and Ollama availability status."""
    detected = await agent.detect_ollama_model()
    return {
        "ollama_running": detected is not None,
        "model": detected or "gemma2:2b (Demo Mode)",
        "mode": "live_ollama" if detected else "demo_simulator",
        "description": (
            f"Active on-device model: {detected}"
            if detected
            else "Ollama not running; using high-fidelity Gemma 2B demo simulator"
        ),
    }


@app.get("/api/vitals")
async def get_vitals() -> Dict[str, Any]:
    """Returns recent vitals and trends from the local database."""
    return {
        "recent_bp": get_recent_bp_readings(5),
        "recent_exercises": get_recent_exercises(5),
        "summary": get_vitals_summary(),
    }


@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    """Streams assistant response chunks, raw Vertical DSL, and compiled wire messages via SSE."""
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    async def event_generator():
        async for event in agent.stream_turn(req.message, req.history):
            data_str = json.dumps(event)
            yield f"data: {data_str}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# Serve built client static files if present
CLIENT_DIST = Path(__file__).resolve().parents[1] / "client" / "dist"
if CLIENT_DIST.exists():
    app.mount("/", StaticFiles(directory=str(CLIENT_DIST), html=True), name="static")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
