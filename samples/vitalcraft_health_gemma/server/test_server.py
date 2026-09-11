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

"""Unit tests verifying VitalCraft server, database, and Vertical format compiler."""

import pytest
from database import get_recent_bp_readings, get_recent_exercises, get_vitals_summary
from tools import tool_build_exercise_plan, tool_get_vitals_summary
from agent import VitalCraftAgent
from mock_responses import SCENARIOS


def test_database_records():
    bp_readings = get_recent_bp_readings(10)
    assert len(bp_readings) == 10
    assert bp_readings[0]["systolic"] == 134
    assert bp_readings[0]["diastolic"] == 86

    exercises = get_recent_exercises(10)
    assert len(exercises) == 10
    assert any(e["activity"] == "Brisk Walking" for e in exercises)

    summary = get_vitals_summary()
    assert "mmHg" in summary["recent_avg_bp"]
    assert summary["recent_workouts_count"] >= 0


def test_agent_catalog_and_prompt():
    agent = VitalCraftAgent()
    prompt = agent.system_prompt
    assert "VitalCraft" in prompt
    # Leaf components must be in signatures
    assert "BloodPressureCard(" in prompt
    assert "ExerciseLogCard(" in prompt
    assert "VitalsTrendChart(" in prompt
    assert "HabitTracker(" in prompt
    assert "HealthPlanBuilder(" in prompt


def test_compiler_on_health_scenarios():
    agent = VitalCraftAgent()
    compiler = agent.compiler

    # Test compilation of default health scenario
    default_text = SCENARIOS["default"]
    msgs = compiler.compile(default_text)
    assert len(msgs) > 0
    # In v0.9.1, each surface has createSurface and updateComponents
    surfaces = [m["createSurface"]["surfaceId"] for m in msgs if "createSurface" in m]
    assert "main" in surfaces
    assert len(surfaces) >= 3  # Multiple components mapped to independent surfaces

    # Check that BloodPressureCard compiled properly
    bp_comp = next(
        c
        for m in msgs
        if "updateComponents" in m
        for c in m["updateComponents"]["components"]
        if c.get("component") == "BloodPressureCard"
    )
    assert bp_comp["systolic"] == 134
    assert bp_comp["diastolic"] == 86
    assert bp_comp["status"] == "Stage 1 Hypertension"

    # Test plan scenario compilation
    plan_text = SCENARIOS["plan"]
    plan_msgs = compiler.compile(plan_text)
    assert len(plan_msgs) > 0
    plan_comp = next(
        c
        for m in plan_msgs
        if "updateComponents" in m
        for c in m["updateComponents"]["components"]
        if c.get("component") == "HealthPlanBuilder"
    )
    assert "Walking Plan" in plan_comp["planTitle"]
    assert len(plan_comp["milestones"]) == 3
