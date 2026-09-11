<!--
 Copyright 2024 Google LLC

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

     https://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
-->

# VitalCraft: Private On-Device Health & Exercise Assistant

VitalCraft is an application demonstrating how Google's lightweight **Gemma 2B** edge model pairs with the **A2UI Vertical inference format** to generate interactive user interfaces directly on a user's device.

All health vitals, exercise records, and model inference run locally on device, keeping personal health information private.

---

## 1. Design Rationale

### Why On-Device Health & Exercise?
Health metrics such as blood pressure logs, heart rate trends, and fitness milestones are personal data. Cloud-based LLM assistants introduce privacy concerns under regulations like HIPAA and GDPR. VitalCraft addresses this by keeping all storage (SQLite/JSON) and model inference on the local host. The assistant operates without sending personal metrics over the internet.

### Why Gemma 2B?
Edge devices require models with small memory footprints and fast generation rates. The 2-billion parameter Gemma model fits easily in system memory (under 2 GB with 4-bit quantization) and runs at interactive speeds on consumer laptops without specialized server accelerators.

### Why the Vertical Inference Format?
Generating full JSON trees for UI protocols on small models presents two major difficulties:
1. **Token Inefficiency**: Full JSON structures spend most of their token budget repeating schema keys, brackets, and quotes. On a 2B model, this wastes time and increases latency. The Vertical format reduces token overhead by approximately 70% by using concise constructor calls:
   ```text
   BloodPressureCard(systolic=134, diastolic=86, status="Stage 1 Hypertension")
   ```
2. **Grammar Reliability**: Small models often drop brackets, emit trailing commas, or produce invalid nested JSON when outputting large schema trees. The Vertical format's flat, Python/Dart-like constructor syntax is familiar to LLMs pre-trained on code, resulting in higher formatting accuracy.
3. **Streamability**: Constructor arguments can be parsed incrementally as tokens arrive, allowing UI components to update on the client before the full model response completes.

### Why Generative UI Over Text Elicitation?
Conversational health apps often fail when they ask open-ended questions in prose (e.g. *"What habits would you like to change today? Review your activity log or set a new fitness goal?"*). This places cognitive load on the user to type descriptions on a keyboard.

VitalCraft uses generative UI components instead:
- Actionable chips ([`MultipleChoiceQuestion`](client/src/catalog/MultipleChoiceQuestion.tsx)) let users select choices with a single click.
- Sliders and rating selectors ([`IntensityPicker`](client/src/catalog/IntensityPicker.tsx)) quantify perceived exertion directly.
- Checklists ([`HealthPlanBuilder`](client/src/catalog/HealthPlanBuilder.tsx), [`HabitTracker`](client/src/catalog/HabitTracker.tsx)) make multi-day routines tangible and trackable.

### Why Dynamic Per-Turn Surface IDs?
A2UI organizes components inside stateful **Surfaces**. In an interactive multi-turn dialogue, if every turn reuses the same surface ID, the client state engine either throws a collision error or overwrites prior UI. VitalCraft assigns each turn a timestamped surface ID (`turn_<timestamp>`). This isolates component state per conversation turn, allowing previous cards and charts to remain active and readable in the chat scrollback.

---

## 2. Architecture & How It Works

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            React Client (Vite)                              │
│                                                                             │
│  ┌───────────────────────┐  ┌──────────────────┐  ┌──────────────────────┐  │
│  │   Chat Conversation   │  │   A2UI Surface   │  │  Health Components   │  │
│  │   Stream & Event Bus  │  │   Host (@a2ui)   │  │  (Cards, Charts, UI) │  │
│  └───────────▲───────────┘  └────────▲─────────┘  └──────────▲───────────┘  │
│              │                       │                       │              │
│              └───────────────────────┴───────────────────────┘              │
│                                      ▲                                      │
│                                      │ SSE Event Stream                     │
└──────────────────────────────────────┼──────────────────────────────────────┘
                                       │ (Text + A2UI Wire JSON)
┌──────────────────────────────────────┴──────────────────────────────────────┐
│                           FastAPI Backend Server                            │
│                                                                             │
│  ┌───────────────────────┐  ┌──────────────────┐  ┌──────────────────────┐  │
│  │  Local Health DB      │  │  Prompt Builder  │  │ VerticalStreamParser │  │
│  │  (20 Vitals Records)  │  │  & Grounding     │  │ (A2UI Core SDK)      │  │
│  └───────────────────────┘  └──────────────────┘  └──────────────────────┘  │
└──────────────────────────────────────▲──────────────────────────────────────┘
                                       │ Streaming HTTP (:11434)
┌──────────────────────────────────────┴──────────────────────────────────────┐
│                               Ollama Runtime                                │
│                     Google Gemma 2B (gemma4:e2b / gemma2:2b)                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Turn Execution Flow

1. **User Action**: The user enters a message or clicks an interactive chip.
2. **Context Injection & Grounding**: The FastAPI backend retrieves the user's latest health metrics (resting blood pressure, workout history, averages) and appends them to Gemma's system prompt along with catalog constructor rules.
3. **Streaming Generation**: Gemma generates a short empathetic text response followed by an `<a2ui>` block with Vertical constructors.
4. **On-the-Fly Compilation**:
   - As tokens arrive from Ollama, the server's [`VerticalStreamParser`](../../agent_sdks/python/src/a2ui/inference_formats/experimental/vertical/stream_parser.py) parses the constructor names and arguments.
   - The parser emits standard A2UI v0.9.1 protocol messages (`createSurface`, `updateComponents`) over Server-Sent Events (SSE).
5. **Client Rendering**:
   - The React client passes the wire messages to `MessageProcessor`.
   - The `MessageProcessor` maps the components against the registered `vitalcraftCatalog`.
   - The components ([`BloodPressureCard`](client/src/catalog/BloodPressureCard.tsx), [`VitalsTrendChart`](client/src/catalog/VitalsTrendChart.tsx), etc.) render inside `<A2uiSurface />`.
6. **Two-Way Interaction**: When a user clicks a choice chip in [`MultipleChoiceQuestion`](client/src/catalog/MultipleChoiceQuestion.tsx), the component dispatches a `vitalcraft:choice-selected` event, triggering the next turn automatically.

---

## 3. Component Catalog

VitalCraft implements 8 custom components declared in [`catalog/health_catalog.json`](catalog/health_catalog.json) and registered in [`client/src/catalog/index.ts`](client/src/catalog/index.ts):

| Component | Description | Example Props |
| :--- | :--- | :--- |
| `BloodPressureCard` | Card displaying systolic, diastolic, pulse, and clinical category | `systolic=134, diastolic=86, status="Stage 1 Hypertension"` |
| `VitalsTrendChart` | SVG line/bar chart for multi-day BP readings or workout minutes | `metric="blood_pressure", systolicValues=[...], targetThreshold=120` |
| `HealthPlanBuilder` | Multi-week cardiovascular plan with interactive milestone checklist | `planTitle="BP Cardio Plan", durationWeeks=4, milestones=[...]` |
| `HabitTracker` | Daily health checklist tracking streaks and completion | `habits=[{"name": "Zone 2 Walk", "streakDays": 5, "completedToday": true}]` |
| `VitalsComparisonTable` | Table contrasting active periods against sedentary baselines | `headers=[...], rows=[...], highlightMetric="Avg Blood Pressure"` |
| `ExerciseLogCard` | Workout log displaying activity, duration, heart rate zone, and calories | `activity="Brisk Walking", durationMinutes=25, avgHeartRate=114` |
| `MultipleChoiceQuestion` | Actionable selection chips for low-friction decision making | `question="How do you feel?", options=["Ready", "Fatigued"]` |
| `IntensityPicker` | Number selector (1–10) for Rate of Perceived Exertion (RPE) | `label="Target Effort", selected=3, min=1, max=10` |

---

## 4. Setup & Running

### Prerequisites

1. **Python 3.10+** with [`uv`](https://docs.astral.sh/uv/)
2. **Node.js 18+** with **Yarn Berry**
3. **Ollama** (optional, recommended for live on-device inference):
   - Install Ollama from [ollama.com](https://ollama.com)
   - Pull and start the Gemma model:
     ```bash
     ollama run gemma4:e2b
     # Alternatively:
     # ollama run gemma2:2b
     ```
   - *Note: If Ollama is not running, VitalCraft automatically falls back to an offline simulated stream.*

### Step 1: Build the Client Assets

From the repository root:

```bash
yarn workspace @a2ui/vitalcraft-client run build
```

To run Vite in hot-reload development mode instead:

```bash
yarn workspace @a2ui/vitalcraft-client run dev
```

### Step 2: Start the Backend Server

From the repository root:

```bash
PYTHONPATH=samples/vitalcraft_health_gemma/server uv run uvicorn app:app \
  --app-dir samples/vitalcraft_health_gemma/server \
  --host 127.0.0.1 \
  --port 8085
```

Open [http://127.0.0.1:8085](http://127.0.0.1:8085) in your web browser.

---

## 5. Automated Testing & Verification

### Unit & Backend Tests

```bash
PYTHONPATH=samples/vitalcraft_health_gemma/server uv run pytest samples/vitalcraft_health_gemma/server/test_server.py
```

### Client Code Hygiene Checks

```bash
yarn workspace @a2ui/vitalcraft-client run lint
yarn workspace @a2ui/vitalcraft-client run format:check
yarn workspace @a2ui/vitalcraft-client run test
```

### End-to-End Puppeteer Test

The automated E2E test runs against a live server, submits queries, verifies that A2UI components render, opens the format inspector, and captures screenshots:

```bash
APP_URL=http://127.0.0.1:8085 yarn workspace @a2ui/vitalcraft-client run e2e
```

Screenshots are saved under `client/screenshots/`:
- `vitalcraft_e2e.png`: Initial blood pressure card and trend chart rendering.
- `vitalcraft_multi_turn_e2e.png`: Follow-up turn showing the interactive health plan builder and intensity selector.
- `vitalcraft_vertical_dsl_e2e.png`: Syntax inspector drawer displaying streaming Vertical DSL tokens.
- `vitalcraft_inspector_e2e.png`: Syntax inspector drawer displaying compiled A2UI Wire JSON messages.
