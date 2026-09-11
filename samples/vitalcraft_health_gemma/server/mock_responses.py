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

"""High-fidelity mock streaming responses for VitalCraft.

Simulates on-device Gemma 2B streaming with authentic Vertical syntax,
enabling offline demonstrations and deterministic testing.
"""

SCENARIOS = {
    "default": """Let's check your recent readings and tailor a safe, heart-healthy routine to bring those numbers down.

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
  question="How are you feeling physically today?",
  options=["Energetic & Ready", "Mildly Fatigued", "Headache or Lightheaded", "Joint Soreness"]
)
MultipleChoiceQuestion(
  question="What low-impact aerobic exercise fits your routine best?",
  options=["Brisk Walking", "Zone 2 Cycling", "Lap Swimming", "Gentle Yoga"]
)
IntensityPicker(
  label="Target Workout Effort (1=Very Light, 5=Moderate, 10=Max)",
  selected=3,
  min=1,
  max=10
)
</a2ui>
""",
    "plan": """Aerobic exercise like brisk walking is clinically proven to lower systolic blood pressure by 5–8 mmHg when done consistently. Here is your personalized starting plan:

<a2ui>
VitalsComparisonTable(
  headers=["Period", "Avg Blood Pressure", "Workouts / Week", "Avg Resting HR"],
  rows=[
    ["Active Cardio Weeks (Aug)", "122 / 79 mmHg", "3.5 sessions", "66 bpm"],
    ["Sedentary Weeks (Sep)", "134 / 86 mmHg", "1.0 session", "74 bpm"]
  ],
  highlightMetric="Avg Blood Pressure"
)
HealthPlanBuilder(
  planTitle="Heart-Healthy 2-Week Walking Plan",
  targetMetric="Goal: Systolic < 125 mmHg",
  durationWeeks=2,
  milestones=[
    "3x 25-min brisk walks in Zone 2 cardio (HR 110-125 bpm)",
    "Log morning blood pressure within 30 mins of waking",
    "Maintain 2.5L daily hydration and reduce sodium below 2,000mg"
  ],
  status="proposed"
)
HabitTracker(
  title="Daily Cardiovascular Habits",
  habits=[
    {"id": "h1", "name": "Morning BP Check", "streakDays": 5, "completedToday": true, "category": "Vitals"},
    {"id": "h2", "name": "25-min Zone 2 Walk", "streakDays": 0, "completedToday": false, "category": "Cardio"},
    {"id": "h3", "name": "Drink 2.5L Water", "streakDays": 3, "completedToday": true, "category": "Hydration"},
    {"id": "h4", "name": "Sodium Under 2,000mg", "streakDays": 2, "completedToday": false, "category": "Nutrition"}
  ]
)
MultipleChoiceQuestion(
  question="Would you like to activate this plan and set daily reminders?",
  options=["Activate Plan & Reminders", "Adjust Plan Goals", "Keep as Reference Only"]
)
</a2ui>
""",
    "exercise": """Here is your recent cardiovascular workout history and weekly movement summary:

<a2ui>
ExerciseLogCard(
  activity="Brisk Walking",
  durationMinutes=25,
  avgHeartRate=114,
  calories=135,
  intensity="Light",
  date="Yesterday, 5:30 PM",
  notes="Neighborhood loop at evening golden hour"
)
ExerciseLogCard(
  activity="Zone 2 Cycling",
  durationMinutes=35,
  avgHeartRate=122,
  calories=230,
  intensity="Moderate",
  date="Sep 6, 2026",
  notes="Stationary bike, kept steady cadence"
)
VitalsTrendChart(
  title="Weekly Exercise Minutes vs Target",
  metric="exercise_minutes",
  labels=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
  exerciseMinutes=[0, 30, 0, 40, 0, 35, 25],
  targetThreshold=30
)
    HabitTracker(
      title="Weekly Activity Consistency",
      habits=[
        {"id": "h1", "name": "150 mins Zone 2 Cardio / Week", "streakDays": 2, "completedToday": true, "category": "Exercise"},
        {"id": "h2", "name": "Post-Workout Hydration", "streakDays": 4, "completedToday": true, "category": "Recovery"}
      ]
    )
    MultipleChoiceQuestion(
      question="What would you like to explore next?",
      options=["Propose 2-week workout plan", "Check blood pressure trend", "Log new workout"]
    )
    </a2ui>
    """,
    "habits": """Based on your health history, regular Zone 2 aerobic exercise and daily morning blood pressure tracking show the strongest clinical correlation with lowering your systolic numbers:

    <a2ui>
    HabitTracker(
      title="Daily Cardiovascular Habits",
      habits=[
        {"id": "h1", "name": "Morning BP Check", "streakDays": 5, "completedToday": true, "category": "Vitals"},
        {"id": "h2", "name": "25-min Zone 2 Walk", "streakDays": 2, "completedToday": false, "category": "Cardio"},
        {"id": "h3", "name": "Drink 2.5L Water", "streakDays": 4, "completedToday": true, "category": "Hydration"},
        {"id": "h4", "name": "Sodium Under 2,000mg", "streakDays": 1, "completedToday": false, "category": "Nutrition"}
      ]
    )
    MultipleChoiceQuestion(
      question="Which habit would you like to build or customize first?",
      options=["25-min Zone 2 Walk", "Morning BP Check Routine", "Sodium & Dietary Adjustments", "View 7-Day Vitals Trend"]
    )
    </a2ui>
    """,
}


def get_mock_scenario(user_message: str) -> str:
    """Selects appropriate scenario based on user input keywords."""
    msg = user_message.lower()
    if any(k in msg for k in ("habit", "focus", "daily", "routine")):
        return SCENARIOS["habits"]
    if any(k in msg for k in ("plan", "walk", "ready", "energetic", "start", "accept")):
        return SCENARIOS["plan"]
    if any(k in msg for k in ("log", "workout", "exercise", "history", "recent")):
        return SCENARIOS["exercise"]
    return SCENARIOS["default"]
