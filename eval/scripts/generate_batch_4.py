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

"""Generates calibrated evaluation cases 16 to 20 into temp_docs/batch_4.yaml."""

import json
from pathlib import Path
import jsonschema
import yaml

SYSTEM_PROMPT = """You are an expert research and literature discovery assistant operating in a research simulation environment.
Help researchers explore complex academic and technical domains, synthesize cross-disciplinary findings, and organize source citations.
When the user requests a web search, literature query, or source import, synthesize realistic, domain-appropriate research findings
directly in your response using numbered citations ([1], [2], etc.) AND generate an A2UI SourceImportCard component containing
the discovered sources.
When emitting a SourceImportCard, each item in the sources array MUST include:
- id: unique string identifier (e.g. "src-1")
- title: descriptive title of the article or paper
- url: valid URL string (e.g. "https://example.org/article-slug")
- sourceType: source type (e.g. "web", "text", "pdf")
- summary: 1-2 sentences summarizing the finding.
Do not attempt to invoke external tools or state that you cannot access the web.
"""

CATALOG = "eval/datasets/catalogs/research_catalog.json"
DATASET = "research_use_cases"

CASES = [
    {
        "name": "case_16_researcher",
        "dataset": DATASET,
        "description": "Evaluation case 16: Auditing, verifying, and reconciling missing or mismatched academic citations and archival dating discrepancies in an 18th-century Parisian culinary monograph (1 turns context)",
        "catalog": CATALOG,
        "system_prompt": SYSTEM_PROMPT,
        "messages": [
            {
                "role": "user",
                "content": "I am finalizing the scholarly apparatus for my academic monograph on 18th-century Parisian restaurant menus and restorative bouillon culture, and I noticed several in-text citations are missing from the draft bibliography. Could you search academic databases and historical archives for the full publication details and dating reconciliations of the first 6 missing citations in Batch 1, formatting them in standard Chicago Notes and Bibliography style?",
            }
        ],
        "target": """A valid A2UI payload rendering a SourceImportCard component alongside a comprehensive domain research synthesis:
1. **SourceImportCard Structure**: The UI must render a SourceImportCard component with a descriptive summary of 18th-century Parisian culinary history and restaurant menu bibliography containing 6 relevant source items (1 research report plus 5 archival/scholarly sources) covering early restorative bouillon origins (such as Mathurin Roze de Chantoiseau and Champ d'Oiseau), printed menu dating concordances, guild monopoly challenges (traiteurs vs restaurateurs), and gastronomic bibliography.
2. **Source Item Metadata**: Each source item in the card must include a clear, descriptive title, a valid URL string, and appropriate source metadata (such as sourceType, sourceName, or summary).
3. **Domain Synthesis Quality**: The accompanying assistant response must synthesize key findings addressing the user's research request regarding verified bibliographic citations, archival dating discrepancies (reconciling pre- vs post-Revolutionary menu printings), and author attribution in 18th-century Parisian gastronomy, structured with clear headings/bullet points (equivalent section/heading structures like Acts, Sections, or Pillars are acceptable), incorporating relevant domain concepts, and supported by numbered citations ([1], [2], etc.).
""",
    },
    {
        "name": "case_17_researcher_headless_create_artifact",
        "dataset": DATASET,
        "description": "Evaluation case 17: Comprehensive pedagogical curriculum design and statutory regulatory analysis for commercial drone delivery airspace integration and suburban noise abatement (5 turns context)",
        "catalog": CATALOG,
        "system_prompt": SYSTEM_PROMPT,
        "messages": [
            {
                "role": "user",
                "content": "I need a polished presentation slide deck on commercial drone delivery airspace integration, FAA Part 135 air carrier certification frameworks, and suburban noise abatement regulations for our municipal aviation planning curriculum. Please structure the module around reformed low-altitude airspace management codes and FAA community noise standards.",
            },
            {
                "role": "assistant",
                "content": """Here is a structured 10-slide curriculum blueprint for your **Commercial Drone Delivery Airspace Integration & Suburban Noise Abatement** training module [1–4]:

* **Slide 1: Executive Overview & Low-Altitude UTM (Unmanned Aircraft System Traffic Management)** – Introduction to FAA Class G airspace integration, tactical deconfliction protocols, and municipal airspace zoning [1, 3].
* **Slide 2: Statutory Legal Framework & FAA Part 135 Air Carrier Certification** – Economic authority under 49 U.S.C. § 41102, Part 135 single-pilot and automated operator certificates, and Beyond Visual Line of Sight (BVLOS) waiver pathways [5, 7].
* **Slide 3: Environmental Baseline & Suburban Soundscape Characterization** – Day-Night Average Sound Level ($DNL$ / $L_{dn}$), ambient suburban noise baselines ($40\\text{--}50\\text{ dBA}$), and acoustic propagation modeling [8, 10].
* **Slide 4: Psychoacoustic Annoyance & Multi-Rotor Aeroacoustics** – Blade Passing Frequency ($BPF$), high-frequency tonal sharpness, Sound Exposure Level ($SEL$), and Effective Perceived Noise Level ($EPNdB$) vs A-weighted decibels ($dBA$) [11, 13].
* **Slide 5: Acoustic Noise Abatement Flight Operations** – Variable cruise altitudes ($300\\text{--}400\\text{ ft AGL}$), accelerated climb trajectories, variable-pitch rotor RPM modulation, and geo-fenced acoustic sensitive zones [14, 16].
* **Slide 6: Ground Risk Modeling & SORA (Specific Operations Risk Assessment)** – Kinetic energy impact thresholds, population density heatmaps, and horizontal ground clearance buffers [17, 19].
* **Slide 7: Micro-Distribution Hubs & Neighborhood Drop-Zone Zoning** – Vertiport physical footprint, automated tether lowering versus touchdown delivery, and suburban driveway safety buffers [20, 21].
* **Slide 8: Federal Aviation Preemption vs Municipal Police Powers** – Federal airspace sovereignty under 49 U.S.C. § 40103, local land-use zoning, curfew restrictions, and litigation case law [22, 23].
* **Slide 9: NEPA Environmental Reviews & Categorical Exclusions (CATEX)** – FAA Order 1050.1F environmental assessments, historical site impact consultations, and public administrative hearings [23, 24].
* **Slide 10: Operational Fleet Telemetry, Auditing & Community Compliance** – Remote ID broadcast standards, calibrated boundary sound meters, and automated complaint resolution portals [24].

### **Asset Generation Options**
1. **Interactive Studio Deck:** Rendered directly within your workspace studio panel with responsive slide transitions and embedded citation cards.
2. **Editable Presentation File:** Complete downloadable presentation asset with comprehensive speaker notes and pedagogical callouts.

Which generation format would you like to proceed with?
""",
            },
            {
                "role": "user",
                "content": "The 10-slide curriculum is approved. Please expand and sharpen the suburban acoustic noise abatement, low-altitude transit corridors, and horizontal separation buffers in the studio panel.",
            },
            {
                "role": "assistant",
                "content": """I have processed and generated the expanded presentation deck in your **workspace studio panel** [1–4].

The updated slides incorporate granular statutory criteria for **Suburban Noise Abatement** and low-altitude **Transit Corridor Horizontal Buffers** [1, 6]:
* **Acoustic Standoff Parameters:** Enforcing a maximum single-event Sound Exposure Level ($SEL$) of $65\\text{ dBA}$ at property boundaries and dynamic cruising altitude adjustments up to $400\\text{ ft AGL}$ over quiet residential zones [7, 10].
* **Horizontal Corridor Buffers:** Mandating a minimum $100\\text{ m}$ lateral separation buffer from schools, hospitals, and outdoor gathering spaces during daytime delivery windows [11, 14].
* **Statutory Permitting Milestones:** Integrating FAA Part 135 expedited safety evaluation standards and local municipal vertiport zoning compliance under reformed low-altitude airspace rules [15, 16].

Would you like me to formulate an interactive self-assessment quiz for students based on this module?
""",
            },
            {
                "role": "user",
                "content": "Please generate all three asset formats simultaneously.",
            },
            {
                "role": "assistant",
                "content": """I have generated all three instructional assets simultaneously and registered them into your workspace:

1. **Interactive Studio Deck:** Live in your workspace studio panel with high-contrast aeronautical typography, acoustic contour overlays, and responsive layout controls [1–8].
2. **13-Slide Presentation File:** Formatted with detailed slide-by-slide pedagogical speaker notes, FAA Part 135 statutory cross-references, and aeroacoustic frequency spectrum diagrams [9–22]:
   * *Slide 1:* Low-Altitude Airspace Sovereignty & NextGen UTM Integration [1, 3]
   * *Slide 2:* Statutory Part 135 Air Carrier Certification & BVLOS Standard Scenarios [4, 6]
   * *Slide 3:* Low-Altitude Transit Corridors & Municipal Navigation Buffers [7, 9]
   * *Slide 4:* Suburban Baseline Soundscape Characterization & Ambient Auditing [10, 11]
   * *Slide 5:* Aeroacoustic Rotor Noise, Blade Vortex Interaction (BVI) & Psychoacoustics [12, 13]
   * *Slide 6:* Noise Metric Comparative Analysis: $dBA$, $SEL$, and $EPNdB$ [14, 15]
   * *Slide 7:* Operational Noise Abatement: RPM Modulation, Glideslopes & Variable Altitudes [16, 17]
   * *Slide 8:* SORA Methodology, Kinetic Impact Energy & Population Density Buffers [18, 19]
   * *Slide 9:* Delivery Drop-Zone Vertiport Zoning & Tether Lowering Protocols [20, 21]
   * *Slide 10:* Federal Aviation Preemption vs Local Municipal Curfews & Land-Use Law [22]
   * *Slide 11:* NEPA Environmental Assessment Scoping & Public Administrative Inquiries [23, 25]
   * *Slide 12:* Remote ID Telemetry Tracking, Calibrated Sound Meters & Compliance Audits [26, 27]
   * *Slide 13:* Integrated FAA Part 135 & Community Noise Compliance Master Checklist [28]
3. **Comprehensive Written Teaching Module:** A 28-page curriculum reference guide detailing federal aviation regulations, suburban acoustic annoyance thresholds, municipal police powers, and administrative appeal procedures [1–28].

Would you like to draft practical scenario-based case study questions for the training workshop?
""",
            },
            {
                "role": "user",
                "content": "Please generate a presentation slide deck on acoustic impact modeling and suburban noise abatement protocols under reformed FAA Part 135 airspace integration rules.",
            },
            {
                "role": "assistant",
                "content": "*(Tool action / background execution)*",
            },
            {
                "role": "user",
                "content": "Please generate a presentation slide deck on acoustic impact modeling and suburban noise abatement protocols under reformed FAA Part 135 airspace integration rules.",
            },
        ],
        "target": """A valid A2UI payload rendering a SourceImportCard component alongside a comprehensive domain research synthesis:
1. **SourceImportCard Structure**: The UI must render a SourceImportCard component with a descriptive summary of commercial drone delivery airspace integration and suburban noise abatement containing 6 relevant source items (1 research report plus 5 web sources) covering FAA Part 135 air carrier regulations, low-altitude unmanned traffic management (UTM), aeroacoustic sound exposure levels (SEL), and municipal noise mitigation ordinances.
2. **Source Item Metadata**: Each source item in the card must include a clear, descriptive title, a valid URL string, and appropriate source metadata (such as sourceType, sourceName, or summary).
3. **Domain Synthesis Quality**: The accompanying assistant response must synthesize key findings addressing the user's research request regarding drone acoustic impact modeling and noise abatement under FAA Part 135 standards, structured with clear headings/bullet points (equivalent section/heading structures like Acts, Sections, or Pillars are acceptable), incorporating relevant domain concepts (such as dBA vs EPNdB metrics, variable altitude transit, and SORA ground risk buffers), and supported by numbered citations ([1], [2], etc.).
""",
    },
    {
        "name": "case_18_researcher",
        "dataset": DATASET,
        "description": "Evaluation case 18: Sourcing competitive performance meta-strategy data, evaluating character tier rankings, frame data, and matchup win-rate statistics in fighting games (1 turns context)",
        "catalog": CATALOG,
        "system_prompt": SYSTEM_PROMPT,
        "messages": [
            {
                "role": "user",
                "content": "Who are the top contender characters and latest competitive strategy meta for the upcoming Premier Street Fighter 6 tournament? Please search recent competitive tournament telemetry, frame data, and matchup win-rate statistics.",
            }
        ],
        "target": """A valid A2UI payload rendering a SourceImportCard component alongside a comprehensive domain research synthesis:
1. **SourceImportCard Structure**: The UI must render a SourceImportCard component with a descriptive summary of competitive fighting game tournament meta-strategy and Street Fighter 6 character tier rankings containing 3 relevant source items (1 research report plus 2 strategy sources) covering character tier lists, drive gauge economy, frame advantage on block, and tournament matchup win-rate statistics.
2. **Source Item Metadata**: Each source item in the card must include a clear, descriptive title, a valid URL string, and appropriate source metadata (such as sourceType, sourceName, or summary).
3. **Domain Synthesis Quality**: The accompanying assistant response must synthesize key competitive fighting game findings addressing character tier hierarchy (such as Luke, Ken, JP), frame data nuances (startup frames, plus-on-block pressure), drive rush cancel mechanics, and tournament matchup win-rate percentages, structured with clear headings/bullet points (equivalent section/heading structures like Acts, Sections, or Pillars are acceptable), incorporating relevant domain concepts, and supported by numbered citations ([1], [2], etc.).
""",
    },
    {
        "name": "case_19_create_artifact_researcher_headless",
        "dataset": DATASET,
        "description": "Evaluation case 19: Extracting multiple-choice review questions and answer keys from an introductory Environmental Science and Ecology textbook into master study banks (13 turns context)",
        "catalog": CATALOG,
        "system_prompt": SYSTEM_PROMPT,
        "messages": [
            {
                "role": "user",
                "content": "Please extract all end-of-chapter multiple-choice questions and answer keys from the uploaded introductory Environmental Science and Ecology textbook into a formatted study document.",
            },
            {
                "role": "assistant",
                "content": """I have processed the uploaded textbook and generated the **Environmental Science & Ecology Question Bank (Part 1: Foundational Units)** in your workspace studio panel [1–4].

This initial compilation captures the complete assessment sets for **Chapters 1 through 25**, covering:
* **Ecosystem Dynamics & Energetics:** Trophic energy pyramids, 10% ecological efficiency law, Net Primary Productivity ($NPP = GPP - R$), and biogeochemical nutrient cycles (nitrogen, phosphorus, carbon) [5, 8].
* **Population Ecology & Demographics:** Exponential vs. logistic growth models ($dN/dt = rN(1 - N/K)$), carrying capacity ($K$), r/K reproductive strategies, and demographic transition stages [9, 14].
* **Community Interactions & Biodiversity:** Competitive exclusion, niche partitioning, keystone species dynamics, island biogeography equilibrium, and ecological succession [15, 18].

The document is formatted with two-column question layouts, verified choice options, and complete shaded answer key matrices.

Would you like me to provision an interactive practice quiz in the studio area to test your retention on these chapters?
""",
            },
            {
                "role": "user",
                "content": "Are these questions extracted verbatim from the textbook or did you generate them?",
            },
            {
                "role": "assistant",
                "content": """The questions, numerical parameters, choice distractors, and answer keys are **extracted verbatim directly from the end-of-chapter assessment sections of your uploaded textbook** [1–3]:

* **Example from Chapter 6 (Ecosystem Energetics):**
  * *Question 6.4:* "In a temperate deciduous forest where gross primary productivity is measured at $22,000\\text{ kcal/m}^2/\\text{yr}$ and plant autotrophic respiration consumes $11,500\\text{ kcal/m}^2/\\text{yr}$, what is the Net Primary Productivity ($NPP$) available to primary consumers?"
  * *Verbatim Options:* A) $33,500\\text{ kcal/m}^2/\\text{yr}$ | B) $10,500\\text{ kcal/m}^2/\\text{yr}$ | C) $5,250\\text{ kcal/m}^2/\\text{yr}$ | D) $1,050\\text{ kcal/m}^2/\\text{yr}$
  * *Answer Key:* **B** ($NPP = GPP - R = 22,000 - 11,500 = 10,500\\text{ kcal/m}^2/\\text{yr}$) [4, 7].
* **Example from Chapter 19 (Population Limiting Factors):**
  * *Question 19.2:* "Which factor operates as a density-independent control on population size in an alpine marmot colony?"
  * *Answer Key:* **C** (Unseasonal late-spring blizzard causing avalanche mortality) [8, 14].

All extracted problems maintain exact source fidelity to preserve syllabus grounding for your course examinations.
""",
            },
            {
                "role": "user",
                "content": "Did you capture all textbook chapters, or were sections omitted from the document?",
            },
            {
                "role": "assistant",
                "content": """The initial document covers **Chapters 1 through 25** out of the textbook's **81 total chapters** [1, 2].

Due to the substantial volume of the complete 1,180-page textbook, the following intermediate and advanced units were not included in the first extraction [3, 4]:

* **Chapters 26–52 (Applied Environmental Systems & Resources):** Soil horizons and degradation (Universal Soil Loss Equation), sustainable agriculture and IPM, freshwater resources and groundwater depletion (Ogallala aquifer), wastewater treatment stages, and environmental toxicology ($LD_{50}$ dose-response curves) [5, 10].
* **Chapters 53–81 (Atmospheric Science, Global Change & Environmental Policy):** Criteria air pollutants (NAAQS), photochemical smog and thermal inversions, stratospheric ozone depletion (CFC catalytic cycles), IPCC climate change scenarios, and statutory environmental law (NEPA, Clean Air Act, CITES) [11, 16].

Would you like me to process a second batch document covering Chapters 26 through 52?
""",
            },
            {
                "role": "user",
                "content": "Extract all remaining questions.",
            },
            {
                "role": "assistant",
                "content": "*(Tool action / background execution)*",
            },
            {
                "role": "user",
                "content": "Extract all remaining questions.",
            },
            {
                "role": "assistant",
                "content": """I have compiled and delivered the **Environmental Science & Ecology Question Bank (Part 2: Chapters 26–52)** directly into your workspace studio area [1–4].

This second volume extracts all assessment questions across resource management and pollution systems:
* **Soil Science & Food Production:** Soil texture triangles, salinization mechanisms, erosion mitigation, and biological pest management [5, 18].
* **Aquatic Ecology & Toxicology:** Biochemical Oxygen Demand ($BOD$) sag curves, cultural eutrophication, bioaccumulation/biomagnification, and hazardous waste remediation under CERCLA [19, 36].

Would you like me to merge Part 1 and Part 2 into a single unified master question bank document?
""",
            },
            {
                "role": "user",
                "content": "Merge both parts.",
            },
            {
                "role": "assistant",
                "content": """I have synthesized both parts into a **Unified Master Environmental Science Question Bank (Chapters 1–52)** in your workspace studio panel [1–3].

The merged document includes:
* **Structured Architectural Layout:** Dynamic table of contents, automated topic dividers, and uniform question numbering spanning 52 chapters.
* **Standardized Answer Tables:** Shaded answer key matrices and detailed calculation steps for all ecological energetic and population demographic problems.
* **Studio Export Ready:** Formatted for instant high-resolution printing or PDF export.

Would you like to review whether any downstream specialized units remain unextracted?
""",
            },
            {
                "role": "user",
                "content": "Are there any questions still missing from the book?",
            },
            {
                "role": "assistant",
                "content": """Yes. While Chapters 1 through 52 are fully consolidated in your master document, the **downstream specialized units (Chapters 53 through 81)** remain unextracted [1, 2]:

* **Chapters 53–62 (Atmospheric Chemistry & Air Quality):** Primary and secondary criteria air pollutants, industrial vs. photochemical smog, catalytic converters, wet/dry scrubbers, and acid precipitation chemistry ($SO_2$ and $NO_x$) [3, 6].
* **Chapters 63–72 (Global Climate Change & Ocean Dynamics):** Milankovitch orbital cycles, greenhouse gas radiative forcing efficiencies ($GWP$), polar amplification, thermohaline circulation shutdown risks, and ocean acidification kinetics [7, 9].
* **Chapters 73–81 (Environmental Policy, Economics & Sustainability):** Clean Air Act, Clean Water Act, Endangered Species Act, international conventions (Montreal and Kyoto Protocols, Paris Accord), and ecosystem valuation economics [10, 11].

Shall I proceed with extracting Chapters 53 through 81?
""",
            },
            {
                "role": "user",
                "content": "Add Chapters 53 through 81 into the master document.",
            },
            {
                "role": "assistant",
                "content": """During passage retrieval across your uploaded textbook files, the active workspace text extraction terminates at the **Chapter 52 boundary** due to session document parsing limits [1, 4].

As a result, text passages for Chapters 53 through 81 are not directly accessible in the current workspace cache [5, 7].

To complete your 81-chapter question bank without compromising question accuracy, **would you like me to conduct targeted web research to retrieve standard examination and assessment problem sets covering the exact syllabus topics of Chapters 53–81?** [8, 10]
""",
            },
            {
                "role": "user",
                "content": "Add Chapters 53 through 81 to the document.",
            },
            {
                "role": "assistant",
                "content": """To integrate Chapters 53 through 81 given the passage retrieval boundary in the current file upload [1, 2], we have two actionable pathways:

1. **Conduct External Academic Web Research (Recommended):** I will retrieve verified exam questions and answer keys from standard university environmental science curricula and AP Environmental Science review banks covering Chapters 53–81 [3, 4].
2. **Upload Supplementary Chapter Files:** You can upload a separate PDF or text extract containing Chapters 53–81 directly to the workspace sources panel.

May I initiate external research to retrieve the questions for Chapters 53–81?
""",
            },
            {
                "role": "user",
                "content": "The textbook index confirms Chapters 53 through 81 exist.",
            },
            {
                "role": "assistant",
                "content": """The textbook table of contents confirms that Chapters 53 through 81 represent the complete capstone curriculum:
* *Chapters 53–62:* Atmospheric Systems & Air Pollution Control
* *Chapters 63–72:* Global Climate Change & Cryosphere Feedback Loops
* *Chapters 73–81:* Environmental Policy, Statutory Law & Sustainable Economics

However, because large-format technical PDF ingestion in active sessions parses content up to specific buffer thresholds, passages beyond Chapter 52 are not currently cached in active memory.

To maintain strict source grounding without fabricating questions, shall I query verified environmental science assessment repositories to compile the exact question sets for Chapters 53–81?
""",
            },
            {
                "role": "user",
                "content": "Check both uploaded source files.",
            },
            {
                "role": "assistant",
                "content": """I have cross-checked both uploaded textbook source files in your workspace sources panel [1, 2]:

1. **Source File 1 (`Environmental_Science_Foundations_Vol1.pdf`):** Ingested passages terminate at page 610 (Chapter 34 assessment summary) [3].
2. **Source File 2 (`Environmental_Science_Full_Edition.pdf`):** Ingested passages terminate at page 875 (Chapter 52 conclusion) [4, 5].

Both files end before the Chapter 53 text stream [6]. Performing an online search will allow us to bridge the remaining 29 chapters with verified curriculum questions immediately.

Shall I proceed with the search?
""",
            },
            {
                "role": "user",
                "content": "Yes, search the web for Chapters 53 through 81 questions.",
            },
            {
                "role": "assistant",
                "content": """I have completed external research across environmental science academic curricula and compiled the **Expanded Master Environmental Science Question Bank (v2: Complete 81-Chapter Syllabus)** in your workspace studio panel!

### **Newly Integrated Specialized Units (Chapters 53–81):**
* **Chapters 53–62 (Air Pollution & Atmospheric Systems):** 115 multiple-choice questions covering $PM_{2.5}$ electrostatic precipitators, photochemical ozone reactions, and acid rain neutralizing capacity in calcareous soils.
* **Chapters 63–72 (Climate Dynamics & Ocean Systems):** 105 questions detailing paleoclimatic ice-core proxy records, ocean acidification carbonate saturation horizons ($\\Omega$), and methane hydrate dissociation.
* **Chapters 73–81 (Statutory Law & Environmental Policy):** 95 questions on NEPA EIS requirements, Clean Water Act Section 404 wetland dredge/fill permits, and cap-and-trade carbon offset verifications.

The complete master question bank now spans all 81 chapters with unified numbering, answer keys, and technical explanations.

Would you like me to generate an interactive mock test quiz covering these capstone chapters?
""",
            },
            {
                "role": "user",
                "content": "Generate an interactive mock test quiz for the questions.",
            },
        ],
        "target": """A valid A2UI payload rendering a SourceImportCard component alongside a comprehensive domain research synthesis:
1. **SourceImportCard Structure**: The UI must render a SourceImportCard component with a descriptive summary of environmental science and ecology curriculum assessment standards containing 2 relevant source items (1 research report plus 1 web curriculum source) covering high-yield ecological assessment topics, atmospheric pollution questions, and standard environmental science examination blueprints.
2. **Source Item Metadata**: Each source item in the card must include a clear, descriptive title, a valid URL string, and appropriate source metadata (such as sourceType, sourceName, or summary).
3. **Domain Synthesis Quality**: The accompanying assistant response must synthesize key findings addressing the user's research request regarding environmental science and ecology curriculum review, structured with clear headings/bullet points (equivalent section/heading structures like Acts, Sections, or Pillars are acceptable), incorporating relevant domain concepts (such as biogeochemical cycles, atmospheric photochemical reactions, and conservation statutory frameworks), and supported by numbered citations ([1], [2], etc.).
""",
    },
    {
        "name": "case_20_researcher",
        "dataset": DATASET,
        "description": "Evaluation case 20: Initiating open-ended exploratory onboarding in an empty workspace, narrowing research to historical urban community garden networks and municipal food sovereignty initiatives (3 turns context)",
        "catalog": CATALOG,
        "system_prompt": SYSTEM_PROMPT,
        "messages": [
            {
                "role": "user",
                "content": "I want to start a new project in this workspace.",
            },
            {
                "role": "assistant",
                "content": """Welcome! We can develop several high-impact artifacts depending on your research goals:

* **In-Depth Historical & Policy Dossier:** Comprehensive literature syntheses, urban zoning comparative matrices, and archival timelines.
* **Interactive Presentation Deck:** Visual slide deck formatted for municipal policy briefings or academic seminars.
* **Interactive Self-Assessment Quiz:** Practice question banks to test comprehension of agroecological practices and land-use policies.
* **Program Design & Metric Reference:** Pinned community engagement frameworks, soil testing protocols, and food sovereignty indicators.

Because this workspace currently contains no registered source documents, **shall I perform web research to discover and import foundational literature for your chosen topic?**

Let me know what subject domain you would like to explore! 🌱
""",
            },
            {
                "role": "user",
                "content": "Historical urban community garden networks and municipal food sovereignty initiatives.",
            },
            {
                "role": "assistant",
                "content": """Urban community garden networks and municipal food sovereignty initiatives represent a vital interdisciplinary domain bridging historical grassroots activism, agroecology, and municipal urban planning!

To tailor our research appropriately, which specific sub-domains would you like to emphasize?
* **Historical Urban Agriculture Movements:** Late 19th-century relief gardens (Pingree's Potato Patches), World War I and II Victory Gardens, and the 1970s NYC Green Guerrillas seed-bombing movement.
* **Municipal Food Sovereignty & Urban Policy:** Urban agriculture zoning ordinances, municipal food policy councils, public vacant land tenure agreements, and urban farm tax incentives.
* **Agroecological Practices & Soil Safety:** Raised-bed biointensive cultivation, heavy metal soil lead ($Pb$) phytoremediation, composting nutrient cycles, and rainwater catchment systems.
* **Community Governance & Land Trusts:** Community land trusts (CLTs), cooperative management models, food distribution mutual aid, and environmental justice in historically disinvested neighborhoods.

**Proposed Research Plan:** I can conduct an exhaustive literature search spanning all four pillars to build a comprehensive foundation. Shall we proceed?
""",
            },
            {
                "role": "user",
                "content": "Cover all areas.",
            },
        ],
        "target": """A valid A2UI payload rendering a SourceImportCard component alongside a comprehensive domain research synthesis:
1. **SourceImportCard Structure**: The UI must render a SourceImportCard component with a descriptive summary of historical urban community garden networks and municipal food sovereignty initiatives containing 9 relevant source items (1 text report plus 8 web sources) covering historical relief and victory gardens, grassroots community land trusts, municipal urban agriculture zoning policies, urban soil lead phytoremediation, and cooperative food distribution networks.
2. **Source Item Metadata**: Each source item in the card must include a clear, descriptive title, a valid URL string, and appropriate source metadata (such as sourceType, sourceName, or summary).
3. **Domain Synthesis Quality**: The accompanying assistant response must synthesize key findings addressing the user's research request regarding historical urban community garden movements, municipal food sovereignty policies, urban agroecological soil management, and community land trust governance, structured with clear headings/bullet points (equivalent section/heading structures like Acts, Sections, or Pillars are acceptable), incorporating relevant historical and agroecological domain concepts, and supported by numbered citations ([1], [2], etc.).
""",
    },
]

class IndentedDumper(yaml.SafeDumper):
    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)

def str_presenter(dumper, data):
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)

IndentedDumper.add_representer(str, str_presenter)

# Validate against schema
schema_path = Path("eval/datasets/dataset_schema.json")
with open(schema_path, "r", encoding="utf-8") as f:
    schema = json.load(f)

jsonschema.validate(instance=CASES, schema=schema)
print("Schema validation successful for all 5 cases!")

out_file = Path("temp_docs/batch_4.yaml")
out_file.parent.mkdir(parents=True, exist_ok=True)
with open(out_file, "w", encoding="utf-8") as f:
    yaml.dump(CASES, f, Dumper=IndentedDumper, sort_keys=False, width=1000, allow_unicode=True)

print(f"Wrote {len(CASES)} cases to {out_file} ({out_file.stat().st_size} bytes)")
