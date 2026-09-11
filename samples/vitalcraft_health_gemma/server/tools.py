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

"""Clinical analysis and planning tools for VitalCraft."""

from typing import Any, Dict, List
from database import get_recent_bp_readings, get_recent_exercises, get_vitals_summary


def tool_get_recent_bp() -> Dict[str, Any]:
    """Retrieves the latest blood pressure readings."""
    readings = get_recent_bp_readings(5)
    latest = readings[0] if readings else None
    return {
        "latest": latest,
        "readings": readings,
        "count": len(readings),
    }


def tool_get_recent_exercises() -> Dict[str, Any]:
    """Retrieves the most recent workout logs."""
    logs = get_recent_exercises(5)
    return {
        "recent_exercises": logs,
        "count": len(logs),
    }


def tool_get_vitals_summary() -> Dict[str, Any]:
    """Retrieves statistical comparisons of blood pressure vs exercise frequency."""
    return get_vitals_summary()


def tool_build_exercise_plan(
    activity: str = "Brisk Walking",
    duration_weeks: int = 2,
    target_reduction: str = "5-8 mmHg",
) -> Dict[str, Any]:
    """Generates a structured cardiovascular habit and exercise plan."""
    return {
        "plan_title": f"Heart-Healthy {duration_weeks}-Week {activity} Plan",
        "target_metric": f"Goal: Reduce Systolic by {target_reduction} (< 125 mmHg)",
        "duration_weeks": duration_weeks,
        "activity": activity,
        "milestones": [
            f"3x 25-min {activity} sessions in Zone 2 cardio (HR 110-125 bpm)",
            "Daily morning blood pressure log within 30 minutes of waking",
            "Maintain 2.5L daily water hydration and reduce sodium below 2,000mg",
        ],
        "status": "proposed",
    }
