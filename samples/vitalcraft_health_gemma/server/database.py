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

"""Local private health database for VitalCraft.

Stores 20 historical health data points (10 blood pressure logs and 10 exercise
sessions) and provides clinical aggregation and filter utilities.
"""

from typing import Any, Dict, List, Optional

HEALTH_RECORDS: List[Dict[str, Any]] = [
    # 10 Blood Pressure Logs (Systolic, Diastolic, Pulse, Stage)
    {
        "id": "bp_1",
        "type": "blood_pressure",
        "date": "2026-09-11",
        "time": "08:15",
        "systolic": 134,
        "diastolic": 86,
        "pulse": 72,
        "context": "morning_resting",
        "stage": "Stage 1 Hypertension",
        "notes": "Felt slight tension in shoulders",
    },
    {
        "id": "bp_2",
        "type": "blood_pressure",
        "date": "2026-09-10",
        "time": "19:40",
        "systolic": 131,
        "diastolic": 85,
        "pulse": 76,
        "context": "evening",
        "stage": "Stage 1 Hypertension",
        "notes": "Post-dinner reading",
    },
    {
        "id": "bp_3",
        "type": "blood_pressure",
        "date": "2026-09-09",
        "time": "08:05",
        "systolic": 138,
        "diastolic": 88,
        "pulse": 79,
        "context": "post_coffee",
        "stage": "Stage 1 Hypertension",
        "notes": "After 2 cups of black coffee",
    },
    {
        "id": "bp_4",
        "type": "blood_pressure",
        "date": "2026-09-08",
        "time": "08:10",
        "systolic": 128,
        "diastolic": 83,
        "pulse": 71,
        "context": "morning_resting",
        "stage": "Elevated",
        "notes": "Good night sleep",
    },
    {
        "id": "bp_5",
        "type": "blood_pressure",
        "date": "2026-09-07",
        "time": "18:50",
        "systolic": 132,
        "diastolic": 84,
        "pulse": 74,
        "context": "evening",
        "stage": "Stage 1 Hypertension",
        "notes": "After work",
    },
    {
        "id": "bp_6",
        "type": "blood_pressure",
        "date": "2026-09-05",
        "time": "08:20",
        "systolic": 125,
        "diastolic": 81,
        "pulse": 68,
        "context": "morning_resting",
        "stage": "Elevated",
        "notes": "Day after 40-minute walk",
    },
    {
        "id": "bp_7",
        "type": "blood_pressure",
        "date": "2026-09-04",
        "time": "08:00",
        "systolic": 124,
        "diastolic": 80,
        "pulse": 67,
        "context": "morning_resting",
        "stage": "Elevated",
        "notes": "Resting heart rate low",
    },
    {
        "id": "bp_8",
        "type": "blood_pressure",
        "date": "2026-09-02",
        "time": "19:15",
        "systolic": 135,
        "diastolic": 87,
        "pulse": 77,
        "context": "evening",
        "stage": "Stage 1 Hypertension",
        "notes": "Stressful workday",
    },
    {
        "id": "bp_9",
        "type": "blood_pressure",
        "date": "2026-08-31",
        "time": "08:10",
        "systolic": 122,
        "diastolic": 79,
        "pulse": 66,
        "context": "morning_resting",
        "stage": "Normal",
        "notes": "Weekend morning",
    },
    {
        "id": "bp_10",
        "type": "blood_pressure",
        "date": "2026-08-29",
        "time": "08:30",
        "systolic": 121,
        "diastolic": 78,
        "pulse": 65,
        "context": "morning_resting",
        "stage": "Normal",
        "notes": "Consistent walking routine active",
    },
    # 10 Exercise Sessions (Activities, Duration, HR, Calories)
    {
        "id": "ex_1",
        "type": "exercise",
        "date": "2026-09-10",
        "activity": "Brisk Walking",
        "duration_min": 25,
        "avg_hr": 114,
        "calories": 135,
        "intensity": "Light",
        "notes": "Neighborhood loop at evening golden hour",
    },
    {
        "id": "ex_2",
        "type": "exercise",
        "date": "2026-09-06",
        "activity": "Zone 2 Cycling",
        "duration_min": 35,
        "avg_hr": 122,
        "calories": 230,
        "intensity": "Moderate",
        "notes": "Stationary bike, kept steady cadence",
    },
    {
        "id": "ex_3",
        "type": "exercise",
        "date": "2026-09-04",
        "activity": "Brisk Walking",
        "duration_min": 40,
        "avg_hr": 118,
        "calories": 210,
        "intensity": "Light",
        "notes": "Felt energetic, BP dropped to 124 next morning",
    },
    {
        "id": "ex_4",
        "type": "exercise",
        "date": "2026-09-01",
        "activity": "Upper Body Strength",
        "duration_min": 30,
        "avg_hr": 115,
        "calories": 160,
        "intensity": "Moderate",
        "notes": "Light dumbbell circuit, avoided straining",
    },
    {
        "id": "ex_5",
        "type": "exercise",
        "date": "2026-08-30",
        "activity": "Lap Swimming",
        "duration_min": 30,
        "avg_hr": 126,
        "calories": 260,
        "intensity": "Moderate",
        "notes": "Relaxed freestyle and backstroke",
    },
    {
        "id": "ex_6",
        "type": "exercise",
        "date": "2026-08-28",
        "activity": "Brisk Walking",
        "duration_min": 35,
        "avg_hr": 116,
        "calories": 190,
        "intensity": "Light",
        "notes": "Morning park stroll",
    },
    {
        "id": "ex_7",
        "type": "exercise",
        "date": "2026-08-26",
        "activity": "Zone 2 Cycling",
        "duration_min": 30,
        "avg_hr": 121,
        "calories": 200,
        "intensity": "Moderate",
        "notes": "Indoor trainer session",
    },
    {
        "id": "ex_8",
        "type": "exercise",
        "date": "2026-08-24",
        "activity": "Gentle Yoga & Mobility",
        "duration_min": 25,
        "avg_hr": 95,
        "calories": 90,
        "intensity": "Light",
        "notes": "Hip mobility and breathwork",
    },
    {
        "id": "ex_9",
        "type": "exercise",
        "date": "2026-08-22",
        "activity": "Brisk Walking",
        "duration_min": 45,
        "avg_hr": 119,
        "calories": 240,
        "intensity": "Light",
        "notes": "Weekend hike on gentle incline",
    },
    {
        "id": "ex_10",
        "type": "exercise",
        "date": "2026-08-20",
        "activity": "Zone 2 Cycling",
        "duration_min": 30,
        "avg_hr": 123,
        "calories": 215,
        "intensity": "Moderate",
        "notes": "Steady aerobic zone",
    },
]


def get_recent_bp_readings(limit: int = 5) -> List[Dict[str, Any]]:
    """Returns the most recent blood pressure readings."""
    bps = [r for r in HEALTH_RECORDS if r["type"] == "blood_pressure"]
    return sorted(bps, key=lambda x: (x["date"], x["time"]), reverse=True)[:limit]


def get_recent_exercises(limit: int = 5) -> List[Dict[str, Any]]:
    """Returns the most recent exercise logs."""
    exs = [r for r in HEALTH_RECORDS if r["type"] == "exercise"]
    return sorted(exs, key=lambda x: x["date"], reverse=True)[:limit]


def get_vitals_summary() -> Dict[str, Any]:
    """Calculates weekly trends comparing active weeks vs recent sedentary weeks."""
    recent_bps = [
        r
        for r in HEALTH_RECORDS
        if r["type"] == "blood_pressure" and r["date"] >= "2026-09-06"
    ]
    older_bps = [
        r
        for r in HEALTH_RECORDS
        if r["type"] == "blood_pressure" and r["date"] < "2026-09-06"
    ]

    recent_systolic = (
        sum(r["systolic"] for r in recent_bps) / len(recent_bps)
        if recent_bps
        else 134
    )
    recent_diastolic = (
        sum(r["diastolic"] for r in recent_bps) / len(recent_bps)
        if recent_bps
        else 86
    )
    recent_pulse = (
        sum(r["pulse"] for r in recent_bps) / len(recent_bps) if recent_bps else 74
    )

    older_systolic = (
        sum(r["systolic"] for r in older_bps) / len(older_bps) if older_bps else 125
    )
    older_diastolic = (
        sum(r["diastolic"] for r in older_bps) / len(older_bps) if older_bps else 81
    )
    older_pulse = (
        sum(r["pulse"] for r in older_bps) / len(older_bps) if older_bps else 68
    )

    recent_ex = [
        r for r in HEALTH_RECORDS if r["type"] == "exercise" and r["date"] >= "2026-09-06"
    ]
    older_ex = [
        r for r in HEALTH_RECORDS if r["type"] == "exercise" and r["date"] < "2026-09-06"
    ]

    return {
        "recent_period": "Past 7 Days (Sedentary)",
        "recent_avg_bp": f"{recent_systolic:.0f} / {recent_diastolic:.0f} mmHg",
        "recent_avg_pulse": f"{recent_pulse:.0f} bpm",
        "recent_workouts_count": len(recent_ex),
        "recent_stage": "Stage 1 Hypertension",
        "older_period": "Prior Weeks (Active Cardio)",
        "older_avg_bp": f"{older_systolic:.0f} / {older_diastolic:.0f} mmHg",
        "older_avg_pulse": f"{older_pulse:.0f} bpm",
        "older_workouts_count": len(older_ex),
        "older_stage": "Elevated / Normal",
        "insight": "Blood pressure was 8-10 mmHg lower during weeks with 3+ Zone 2 walking/cycling sessions.",
    }
