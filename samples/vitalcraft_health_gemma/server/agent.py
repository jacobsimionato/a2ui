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

"""VitalCraft Health Assistant Agent with Gemma and Vertical inference format."""

import asyncio
import json
import os
import re
import time
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, List, Optional
import httpx

from a2ui.core.catalog import Catalog
from a2ui.inference_formats.experimental.vertical import (
    VerticalCompiler,
    VerticalFormat,
    VerticalStreamParser,
)
from mock_responses import get_mock_scenario
from database import get_recent_bp_readings, get_recent_exercises, get_vitals_summary

CATALOG_PATH = Path(__file__).resolve().parents[1] / "catalog" / "health_catalog.json"
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
DEFAULT_MODEL = os.environ.get("GEMMA_MODEL", "gemma4:e2b")


class VitalCraftAgent:
    """Agent that consults local health records and outputs Vertical UI via Gemma."""

    def __init__(self, catalog_path: Path = CATALOG_PATH):
        with open(catalog_path, "r", encoding="utf-8") as f:
            catalog_dict = json.load(f)

        self.catalog = Catalog.from_json(catalog_dict, spec_version="0.9.1")
        self.vertical_format = VerticalFormat(
            catalog=self.catalog, surface_id="main", version="v0.9.1"
        )
        self.compiler = VerticalCompiler(self.catalog, surface_id="main", version="v0.9.1")
        self.prompt_generator = self.vertical_format.prompt_generator

        # Summary of local data for grounding
        recent_bp = get_recent_bp_readings(1)[0]
        vitals_summary = get_vitals_summary()

        self.system_prompt = f"""You are VitalCraft, an empathetic, private, on-device cardiovascular health and exercise companion powered by Gemma.
You have direct read access to the user's private local health database.

### Current User Health Snapshot:
- Most Recent Blood Pressure: {recent_bp['systolic']} / {recent_bp['diastolic']} mmHg (Pulse: {recent_bp['pulse']} bpm, {recent_bp['stage']}) recorded on {recent_bp['date']} at {recent_bp['time']}.
- Recent Trend: {vitals_summary['recent_avg_bp']} over past 7 days ({vitals_summary['recent_workouts_count']} workouts) vs {vitals_summary['older_avg_bp']} when active.
- Clinical Insight: {vitals_summary['insight']}

{self.prompt_generator.generate_system_prompt()}

### MANDATORY INTERACTION & GENERATIVE UI RULES:
1. **NEVER ASK QUESTIONS OR OFFER OPTIONS PURELY IN PROSE.**
   Whenever you ask "what would you like to do?", "how can I help?", "what habits do you want to change?", or suggest next steps, YOU MUST ALWAYS emit an <a2ui> block containing a `MultipleChoiceQuestion` component with rich, actionable option chips!
2. **Always ground your response in the user's local vitals data.**
3. **Format strictly inside `<a2ui>` and `</a2ui>` tags** using concise Vertical constructor calls. Do not output layout containers or raw JSON.
4. **Always combine textual empathy with interactive UI elements** (e.g. BloodPressureCard, VitalsTrendChart, HealthPlanBuilder, HabitTracker, MultipleChoiceQuestion, IntensityPicker).

### FEW-SHOT EXAMPLES OF REQUIRED INTERACTIONS:

Example 1: Getting started, habit inquiry, or general question
User: What daily heart-health habits should I focus on?
Assistant: Based on your health history, regular Zone 2 aerobic exercise and daily morning blood pressure tracking show the strongest clinical impact on keeping your numbers in a healthy range.
<a2ui>
HabitTracker(
  title="Key Cardiovascular Habits",
  habits=[
    {{"id": "h1", "name": "30-min Zone 2 Walk", "streakDays": 2, "completedToday": false, "category": "Exercise"}},
    {{"id": "h2", "name": "Morning Resting BP Log", "streakDays": 5, "completedToday": true, "category": "Vitals"}},
    {{"id": "h3", "name": "Hydration (2.5L Water)", "streakDays": 4, "completedToday": true, "category": "Nutrition"}},
    {{"id": "h4", "name": "Sodium Under 2,000mg", "streakDays": 1, "completedToday": false, "category": "Nutrition"}}
  ]
)
MultipleChoiceQuestion(
  question="Which habit would you like to build or customize first?",
  options=["30-min Zone 2 Walk", "Morning BP Logging Routine", "Sodium & Dietary Adjustments", "View 7-Day Vitals Trend"]
)
</a2ui>

Example 2: Reviewing vitals, blood pressure, or trends
User: Show my recent blood pressure logs and 7-day trend
Assistant: Here is your most recent blood pressure reading and your 7-day trend. Your resting systolic was 134 mmHg this morning, which falls into Stage 1 Hypertension.
<a2ui>
BloodPressureCard(
  systolic=134,
  diastolic=86,
  pulse=72,
  status="Stage 1 Hypertension",
  trend="+4 mmHg vs 7-day average",
  recordedAt="Today, 8:15 AM"
)
VitalsTrendChart(
  title="7-Day Blood Pressure Trend (Morning Readings)",
  metric="blood_pressure",
  labels=["Sep 5", "Sep 6", "Sep 7", "Sep 8", "Sep 9", "Sep 10", "Sep 11"],
  systolicValues=[125, 126, 132, 128, 138, 131, 134],
  diastolicValues=[81, 82, 84, 83, 88, 85, 86],
  targetThreshold=120
)
MultipleChoiceQuestion(
  question="What would you like to do next with this data?",
  options=["Compare against active workout weeks", "Build a workout plan to lower BP", "Log a new blood pressure reading"]
)
</a2ui>

Example 3: Creating workout plans or goals
User: Compare my vitals and propose a 2-week cardiovascular workout plan
Assistant: Comparing your history shows that during weeks with 3+ Zone 2 walking sessions, your blood pressure averaged 122/79 mmHg. Here is a 2-week cardio plan to help you return to that baseline:
<a2ui>
VitalsComparisonTable(
  headers=["Period", "Avg Blood Pressure", "Workouts / Week", "Avg Resting HR"],
  rows=[["Active Cardio Weeks (Aug)", "122 / 79 mmHg", "3.5 sessions", "66 bpm"], ["Sedentary Weeks (Sep)", "134 / 86 mmHg", "1.0 session", "74 bpm"]],
  highlightMetric="Avg Blood Pressure"
)
HealthPlanBuilder(
  planTitle="Heart-Healthy 2-Week Walking Plan",
  targetMetric="Goal: Systolic < 125 mmHg",
  durationWeeks=2,
  milestones=["3x 25-min brisk walks in Zone 2 cardio (HR 110-125 bpm)", "Log morning blood pressure within 30 mins of waking", "Maintain 2.5L daily hydration and reduce sodium below 2,000mg"],
  status="proposed"
)
IntensityPicker(
  label="Target Workout Effort (1=Light, 5=Moderate, 10=Max)",
  selected=3,
  min=1,
  max=10
)
MultipleChoiceQuestion(
  question="Would you like to activate this plan and set daily reminders?",
  options=["Activate Plan & Reminders", "Adjust Plan Goals", "Keep as Reference Only"]
)
</a2ui>
"""

    async def detect_ollama_model(self) -> Optional[str]:
        """Checks if Ollama is running and has a Gemma model available."""
        try:
            async with httpx.AsyncClient(timeout=1.5) as client:
                res = await client.get(f"{OLLAMA_URL}/api/tags")
                if res.status_code == 200:
                    data = res.json()
                    models = [m["name"] for m in data.get("models", [])]
                    for preferred in (DEFAULT_MODEL, "gemma4:e2b", "gemma2:2b", "gemma:2b"):
                        for m in models:
                            if m == preferred or m.startswith(preferred.split(":")[0]):
                                return m
                    if models:
                        return models[0]
        except Exception:
            pass
        return None

    async def stream_turn(
        self, user_message: str, history: Optional[List[Dict[str, str]]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Streams assistant tokens, parses Vertical syntax, and yields real-time UI events."""
        start_time = time.perf_counter()
        turn_id = f"turn_{int(time.time() * 1000)}"
        active_model = await self.detect_ollama_model()

        stream_parser = VerticalStreamParser(
            catalog=self.catalog, surface_id=turn_id, version="v0.9.1"
        )

        accumulated_text = ""
        accumulated_vertical = ""
        raw_response = ""
        tokens_emitted = 0

        if active_model:
            # Connect to local Ollama runtime
            prompt_content = f"{self.system_prompt}\n\nUser: {user_message}\nAssistant:"
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    async with client.stream(
                        "POST",
                        f"{OLLAMA_URL}/api/generate",
                        json={
                            "model": active_model,
                            "prompt": prompt_content,
                            "stream": True,
                            "options": {
                                "temperature": 0.2,
                                "top_p": 0.95,
                            },
                        },
                    ) as response:
                        async for line in response.aiter_lines():
                            if not line:
                                continue
                            data = json.loads(line)
                            chunk = data.get("response", "")
                            if not chunk:
                                continue

                            raw_response += chunk
                            tokens_emitted += 1
                            elapsed = time.perf_counter() - start_time

                            # Process chunk through Vertical stream parser
                            parts = stream_parser.process_chunk(chunk)
                            for part in parts:
                                if part.text:
                                    accumulated_text += part.text
                                    yield {
                                        "type": "text",
                                        "content": part.text,
                                        "elapsed": round(elapsed, 2),
                                    }
                                if part.a2ui_json:
                                    yield {
                                        "type": "a2ui_wire",
                                        "messages": part.a2ui_json,
                                        "elapsed": round(elapsed, 2),
                                    }

                        # Flush remaining buffer on EOF
                        final_parts = stream_parser.process_chunk("")
                        for part in final_parts:
                            if part.a2ui_json:
                                yield {
                                    "type": "a2ui_wire",
                                    "messages": part.a2ui_json,
                                    "elapsed": round(time.perf_counter() - start_time, 2),
                                }

                        match = re.search(r"<a2ui>(.*?)(?:</a2ui>|$)", raw_response, re.DOTALL)
                        accumulated_vertical = match.group(1).strip() if match else ""

                        total_time = time.perf_counter() - start_time
                        yield {
                            "type": "metadata",
                            "model": f"{active_model} (Local Ollama)",
                            "latency_sec": round(total_time, 2),
                            "tokens": tokens_emitted,
                            "raw_vertical": accumulated_vertical,
                        }
                        return
            except Exception as e:
                # If Ollama fails midway or rejects prompt, fallback gracefully to mock scenario
                print(f"[Ollama stream error, switching to mock: {e}]")

        # Fallback to high-fidelity mock scenario
        stream_parser = VerticalStreamParser(
            catalog=self.catalog,
            surface_id=f"turn_{int(time.time() * 1000)}",
            version="v0.9.1",
        )
        scenario_text = get_mock_scenario(user_message)
        chunks = [
            scenario_text[i : i + 24] for i in range(0, len(scenario_text), 24)
        ]

        for chunk in chunks:
            await asyncio.sleep(0.04)  # Simulate on-device token streaming speed (~25 tok/s)
            tokens_emitted += len(chunk.split())
            elapsed = time.perf_counter() - start_time

            parts = stream_parser.process_chunk(chunk)
            for part in parts:
                if part.text:
                    accumulated_text += part.text
                    yield {
                        "type": "text",
                        "content": part.text,
                        "elapsed": round(elapsed, 2),
                    }
                if part.a2ui_json:
                    yield {
                        "type": "a2ui_wire",
                        "messages": part.a2ui_json,
                        "elapsed": round(elapsed, 2),
                    }

        final_parts = stream_parser.process_chunk("")
        for part in final_parts:
            if part.a2ui_json:
                yield {
                    "type": "a2ui_wire",
                    "messages": part.a2ui_json,
                    "elapsed": round(time.perf_counter() - start_time, 2),
                }

        match = re.search(r"<a2ui>(.*?)(?:</a2ui>|$)", scenario_text, re.DOTALL)
        accumulated_vertical = match.group(1).strip() if match else ""

        total_time = time.perf_counter() - start_time
        yield {
            "type": "metadata",
            "model": "gemma2:2b (On-Device Demo)",
            "latency_sec": round(total_time, 2),
            "tokens": tokens_emitted,
            "raw_vertical": accumulated_vertical,
        }
