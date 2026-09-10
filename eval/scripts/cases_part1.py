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

"""Synthetic evaluation cases 01 to 10."""

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

CASES_PART_1 = [
    # Case 01
    {
        "name": "case_01_researcher",
        "dataset": DATASET,
        "description": "Evaluation case 01: Ingesting external materials database into workspace, adapting technical refractory formulation plans under strict rare-earth exclusion constraints (4 turns context)",
        "catalog": CATALOG,
        "system_prompt": SYSTEM_PROMPT,
        "messages": [
            {
                "role": "user",
                "content": "Can I share a URL link to refractory coating formulations I recorded in my Digital Materials Vault and use it as a source here? https://materials-vault.aero.example.org/share/7c2d9e1f54a320b?token=spec_link",
            },
            {
                "role": "assistant",
                "content": """**Yes, you can use the URL of formulations recorded in your Digital Materials Vault as a source!**
However, when linking external materials vault repositories, please keep these **important guidelines** in mind:

1. **The page must be set to \"Public Web Sharing\"**: The Research Assistant cannot read authenticated enterprise databases. You must navigate to \"Share\" settings in your materials vault and enable **\"Public link sharing\"** so anyone with the URL can inspect the specification.
2. **How to add the source**:
   * **Manual addition**: Open the \"Sources\" drawer on the left panel, select \"Add Source\" -> \"Web Resource\", and enter the URL.
   * **Direct chat instruction**: Tell me, \"Please add this URL as a source,\" and I will register it directly into this workspace.""",
            },
            {
                "role": "user",
                "content": "Please add this source: https://materials-vault.aero.example.org/collection/cmc-barrier-coatings?token=spec_link",
            },
            {
                "role": "assistant",
                "content": """I have registered the new materials collection (**cmc-barrier-coatings**) as an **active source in your propulsion workspace!**
The assistant can now reference the ceramic matrix composite coating datasheets indexed in this resource.""",
            },
            {
                "role": "user",
                "content": """We are engineering a thermal barrier coating for a hypersonic turbine shroud operating at continuous 1,400 deg C. Due to strict defense export control and supply chain mandates, we have two severe exclusion constraints: zero rare-earth dopants (absolutely no yttrium, ytterbium, or gadolinium) and zero free-silica phase formation to prevent pesting degradation. Can you formulate a customized refractory coating plan that avoids rare-earths and silica while maintaining thermal shock resistance?""",
            },
            {
                "role": "assistant",
                "content": """Regarding the materials database source you added (cmc-barrier-coatings), due to client-side script rendering constraints, only the fallback text \"JavaScript must be enabled to view interactive WebGL materials datasheets...\" could be retrieved [1]. The assistant cannot directly inspect the specific chemical ratios in that file.

Would you like me to conduct an external technical literature search for rare-earth-free refractory ceramic formulations and bond-coat architectures designed for 1,400 deg C environments?""",
            },
            {
                "role": "user",
                "content": "Please search the technical literature for rare-earth-free coating formulations.",
            },
        ],
        "target": """A valid A2UI payload rendering a SourceImportCard component alongside a comprehensive domain research synthesis:
1. **SourceImportCard Structure**: The UI must render a SourceImportCard component with a descriptive summary of rare-earth-free high-temperature ceramic matrix composite (CMC) barrier coating formulation planning containing relevant source items (typically 2–5 sources) covering zirconate-spinel phase stabilizers, refractory oxide bond coats, and quantitative thermal expansion matching formulas.
2. **Source Item Metadata**: Each source item in the card must include a clear, descriptive title, a valid URL string, and appropriate source metadata (such as sourceType, sourceName, or summary).
3. **Domain Synthesis Quality**: The accompanying assistant response must synthesize key findings addressing the user's research request regarding rare-earth-free CMC thermal barrier formulation planning, structured with clear headings/bullet points (equivalent section/heading structures like Phases, Sections, or Pillars are acceptable), incorporating relevant domain concepts, and supported by numbered citations ([1], [2], etc.).""",
    },

    # Case 02
    {
        "name": "case_02_researcher",
        "dataset": DATASET,
        "description": "Evaluation case 02: Investigating deep-sea hydrothermal vent geochemical plume dispersion models with formal reporting verbs and academic citations (2 turns context)",
        "catalog": CATALOG,
        "system_prompt": SYSTEM_PROMPT,
        "messages": [
            {
                "role": "user",
                "content": "Could you analyze the seminal hydrodynamic model of hydrothermal buoyant plume rise formulated by Morton, Taylor, and Turner (1956), contrasting it against Lupton's helium-3 tracer transport observations? Please use formal reporting verbs (e.g. contends, demonstrates, establishes) and parenthetical citations in (Author, Year, p. XX) format.",
            },
            {
                "role": "assistant",
                "content": """The uploaded oceanographic archive document (**Hydrothermal_Plume_Dynamics_Survey.pdf**) contains corrupted OCR scan layers in the buoyant jet section, so specific page numbers and passage transcriptions cannot be verified directly from the current workspace context.

Rather than speculating on exact historical page numbers or equations, I can perform a targeted technical literature search covering Morton, Taylor, and Turner's entrainment hypothesis alongside Lupton's mantle helium-3 tracer dispersion surveys. Would you like me to proceed with this search?""",
            },
            {
                "role": "user",
                "content": "Yes, please execute the web search, ensuring all retrieved analyses include formal reporting verbs and exact bibliographic citations.",
            },
        ],
        "target": """A valid A2UI payload rendering a SourceImportCard component alongside a comprehensive domain research synthesis:
1. **SourceImportCard Structure**: The UI must render a SourceImportCard component with a descriptive summary of deep-sea hydrothermal vent buoyant plume dispersion models containing 5 relevant source items (1 text report slot plus 4 web sources) covering turbulent entrainment mechanics, helium-3 isotope tracer transport, and benthic eddy diffusion.
2. **Source Item Metadata**: Each source item in the card must include a clear, descriptive title, a valid URL string, and appropriate source metadata (such as sourceType, sourceName, or summary).
3. **Domain Synthesis Quality**: The accompanying assistant response must synthesize key oceanographic findings addressing the Morton-Taylor-Turner model versus tracer observations, structured across 4 core conceptual pillars using formal reporting verbs (e.g., demonstrates, establishes, posits) and standardized parenthetical citations (Author, Year, p. XX), supported by numbered citations ([1], [2], etc.).""",
    },

    # Case 03
    {
        "name": "case_03_researcher",
        "dataset": DATASET,
        "description": "Evaluation case 03: Evaluating and integrating subterranean mining autonomous exploration drones and SAR sensor payloads (2 turns context)",
        "catalog": CATALOG,
        "system_prompt": SYSTEM_PROMPT,
        "messages": [
            {
                "role": "user",
                "content": "We have selected the SubTerran Scout-X4 autonomous mapping drone for underground stoping inspections. What complementary lightweight sensor suites can we integrate for pre-blasting void volumetric analysis?",
            },
            {
                "role": "assistant",
                "content": """The **SubTerran Scout-X4** is an agile quadrotor platform with integrated LiDAR SLAM and forward-facing stereoscopic cameras, making it well-suited for GPS-denied underground stope inspection [1-4].

Key baseline capabilities include:
* **LiDAR SLAM Navigational Autonomy**: Real-time 300,000 pts/sec point-cloud generation with sub-centimeter volumetric precision in unlit stopes [2].
* **Collision Avoidance Shielding**: Omnidirectional 360-degree acoustic and optical time-of-flight proximity detection down to 0.15 m [3].
* **Payload Constraints**: Maximum auxiliary payload capacity of 1.25 kg with a 24V regulated power rail and USB-C telemetry uplink [4].

Would you like to explore complementary sensors such as ultra-wideband synthetic aperture radar (SAR) or thermal radiometers to detect unexploded charges and micro-fracture heating before blasting?""",
            },
            {
                "role": "user",
                "content": "We want to incorporate lightweight ground-penetrating radar and synthetic aperture radar payloads for structural rock-mass integrity evaluation prior to physical ore extraction. Can you recommend proven market hardware and zero-code CAD/telemetry ingestion workflows?",
            },
        ],
        "target": """A valid A2UI payload rendering a SourceImportCard component alongside a comprehensive domain research synthesis:
1. **SourceImportCard Structure**: The UI must render a SourceImportCard component with a descriptive summary of subterranean mining drone sensor integration containing 5 relevant source items (1 text report slot plus 4 web sources) covering lightweight SAR payloads, void volumetric modeling, and telemetry streaming pipelines.
2. **Source Item Metadata**: Each source item in the card must include a clear, descriptive title, a valid URL string, and appropriate source metadata (such as sourceType, sourceName, or summary).
3. **Domain Synthesis Quality**: The accompanying assistant response must synthesize key engineering findings across 5 distinct workflow themes (e.g., payload weight budgeting, no-code spatial point-cloud CAD pipelines, enterprise radar pods, and iteration time reduction metrics), supported by numbered citations ([1], [2], etc.).""",
    },

    # Case 04
    {
        "name": "case_04_researcher",
        "dataset": DATASET,
        "description": "Evaluation case 04: Commercial maritime shipping route logistics optimization based on seasonal cyclone corridors and IMO CII carbon compliance tiers (3 turns context)",
        "catalog": CATALOG,
        "system_prompt": SYSTEM_PROMPT,
        "messages": [
            {
                "role": "user",
                "content": "What is the recommended departure window for a Handymax bulk carrier sailing from Singapore to Dampier in late October to avoid monsoonal squall lines?",
            },
            {
                "role": "assistant",
                "content": """Based on historical nautical climatology and regional oceanographic voyage data, a **departure window between October 24 and October 27** is optimal for the Singapore to Dampier transit [1-3].

**Key Logistical and Meteorological Factors:**
* **Intertropical Convergence Zone (ITCZ) Transition**: Late October represents the seasonal lull between the Southwest and Northeast monsoons in the Java Sea, minimizing convective squall frequency [1].
* **Current Routing via Lombok Strait**: Transiting via the Lombok Strait rather than Sunda Strait provides favorable south-setting tidal streams averaging 2.5 to 3.8 knots, reducing voyage duration by approximately 18 hours [2].
* **Northwest Shelf Swell Windows**: Arriving at Dampier prior to the onset of early Southern Hemisphere tropical depression formation preserves safe anchorage maneuverability [3].""",
            },
            {
                "role": "user",
                "content": "Our charterer wants to add a supplementary heavy deck cargo container parcel, but our voyage charter booking was locked under basic IMO Tier II parameters. What are the carrier demurrage and carbon intensity penalty rules if we exceed the deadweight tier?",
            },
            {
                "role": "assistant",
                "content": """The current voyage records in this workspace do not contain the specific charter party rider clauses or vessel-specific Energy Efficiency Existing Ship Index (EEXI) compliance curves [1, 2].

I can perform a targeted maritime regulatory search covering BIMCO standard carbon emission penalty clauses, IMO Carbon Intensity Indicator (CII) correction factors, and post-booking deadweight supplement schedules. Would you like me to initiate this search?""",
            },
            {
                "role": "user",
                "content": "Yes, please execute the search on maritime carbon compliance tiers and supplemental cargo penalties.",
            },
        ],
        "target": """A valid A2UI payload rendering a SourceImportCard component alongside a comprehensive domain research synthesis:
1. **SourceImportCard Structure**: The UI must render a SourceImportCard component with a descriptive summary of maritime shipping route optimization and IMO CII carbon compliance tiers containing 4 relevant source items (typically 1 text report and 3 web sources) covering voyage speed reduction trade-offs, BIMCO carbon clauses, and deadweight surcharge structures.
2. **Source Item Metadata**: Each source item in the card must include a clear, descriptive title, a valid URL string, and appropriate source metadata (such as sourceType, sourceName, or summary).
3. **Domain Synthesis Quality**: The accompanying assistant response must synthesize key findings addressing maritime routing and emission tier trade-offs, structured around 3 core regulatory/logistical principles, supported by numbered citations ([1], [2], etc.).""",
    },

    # Case 05
    {
        "name": "case_05_researcher",
        "dataset": DATASET,
        "description": "Evaluation case 05: Locating, translating, and bibliographically authenticating Renaissance microtonal keyboard temperament treatises (3 turns context)",
        "catalog": CATALOG,
        "system_prompt": SYSTEM_PROMPT,
        "messages": [
            {
                "role": "user",
                "content": """In Nicola Vicentino's 1555 treatise 'L'antica musica ridotta alla moderna prattica', there is a discussion on dividing the whole tone into five fifth-tones (dieses) for the 31-tone archicembalo keyboard. Can you locate the exact Italian phrasing and page number from our manuscript PDF?""",
            },
            {
                "role": "assistant",
                "content": """The uploaded facsimile document (**Vicentino_Antica_Musica_1555.pdf**) contains un-indexed high-contrast woodblock plates that lack digitized optical character recognition text in the fifth-tone division chapter.

I can perform an external scholarly literature search in historical musicology databases to locate the exact 1555 Venetian Italian text, Book and Chapter citations, and modern cents interval calculations for the 31-tone chromatic system. Would you like me to search for this?""",
            },
            {
                "role": "user",
                "content": "Please check this scholarly manuscript digital edition: https://archival-musicology.example.org/editions/vicentino-1555-treatise.pdf",
            },
            {
                "role": "assistant",
                "content": """The external domain `archival-musicology.example.org` restricts automated scraper access through an institutional proxy gateway, preventing direct document ingestion from that URL. The local copy in our workspace remains unindexed.

I recommend running a targeted academic search across open-access musicology repositories for the verbatim Italian definition of the *comma enarmonico* and the 31-step archicembalo temperament. Shall I proceed?""",
            },
            {
                "role": "user",
                "content": "Yes, please execute the search.",
            },
        ],
        "target": """A valid A2UI payload rendering a SourceImportCard component alongside a comprehensive domain research synthesis:
1. **SourceImportCard Structure**: The UI must render a SourceImportCard component with a descriptive summary of Renaissance microtonal tuning systems and archicembalo keyboard temperaments containing 4 relevant source items (1 text report slot plus 3 web sources) covering Nicola Vicentino's 31-tone division, cents tuning ratios, and historical Italian treatise citations.
2. **Source Item Metadata**: Each source item in the card must include a clear, descriptive title, a valid URL string, and appropriate source metadata (such as sourceType, sourceName, or summary).
3. **Domain Synthesis Quality**: The accompanying assistant response must synthesize key musicological findings, presenting the exact historical context, Italian terminology, mathematical division of the tone, and authoritative bibliographic references, supported by numbered citations ([1], [2], etc.).""",
    },

    # Case 06
    {
        "name": "case_06_researcher",
        "dataset": DATASET,
        "description": "Evaluation case 06: Structuring civil engineering bridge seismic retrofit coursework linking lecture slides to post-earthquake failure investigation reports (4 turns context)",
        "catalog": CATALOG,
        "system_prompt": SYSTEM_PROMPT,
        "messages": [
            {
                "role": "user",
                "content": "We need to build a comprehensive university lecture syllabus module on 'Seismic Retrofit of Multi-Column Highway Overpass Bents'. Can you outline the module based on our textbook slides?",
            },
            {
                "role": "assistant",
                "content": """Based on the structural mechanics textbook slides loaded in this workspace, here is an outline for the **Seismic Retrofit of Highway Overpass Bents** module [1-4]:

* **Week 1: Ductility Demands and Plastic Hinging**: Moment-curvature analysis of reinforced concrete piers, confined vs unconfined concrete stress-strain relationships [1].
* **Week 2: Shear Failure Mechanisms in Short Columns**: Brittle shear vs flexural failure modes, shear demand amplification under transverse ground motions [2].
* **Week 3: Jacketing and Confinement Technologies**: Steel plate jacketing, fiber-reinforced polymer (FRP) composites, and reinforced concrete overlays [3].
* **Week 4: Foundation Rocking and Column Base Connections**: Soil-structure interaction, micropile pinning, and elastomeric base isolation bearing retrofits [4].""",
            },
            {
                "role": "user",
                "content": "Can we link Week 2 directly to forensic engineering findings from real bridge failures, specifically the Hanshin Expressway collapse during the 1995 Kobe earthquake?",
            },
            {
                "role": "assistant",
                "content": """Integrating the Hanshin Expressway Route 3 (Fukae section) collapse provides a powerful forensic case study for Week 2 [1, 2].

**Key Forensic Lessons for the Syllabus:**
1. **Premature Longitudinal Reinforcement Cutoff**: Inadequate termination development length of primary rebar led to localized flexural-shear failure at 2.5 meters above footing [1].
2. **Inadequate Transverse Hoop Confinement**: Spacing of 90-degree bend ties proved unable to confine core concrete after spalling of exterior cover [2].
3. **Massive Overturning Demand**: The 18-pier single-column viaduct suffered complete toppling under near-fault vertical and horizontal accelerations exceeding 0.8g.""",
            },
            {
                "role": "user",
                "content": "We also need to incorporate recent high-damping elastomeric rubber bearing (HDRB) shear strain limits from recent bridge engineering incident bulletins. Are those in our workspace?",
            },
            {
                "role": "assistant",
                "content": """The current workspace slides discuss traditional lead-rubber bearings (LRBs) but do not contain recent engineering technical bulletins on high-damping rubber bearing (HDRB) aging degradation or post-2020 AASHTO shear strain limit updates [1].

Would you like me to search external structural engineering databases for recent peer-reviewed investigations into HDRB ultimate shear failure under subduction zone earthquake ground motions?""",
            },
            {
                "role": "user",
                "content": "Yes, please retrieve recent forensic engineering reports and AASHTO updates on HDRB elastomeric isolator performance under near-fault ground motions.",
            },
        ],
        "target": """A valid A2UI payload rendering a SourceImportCard component alongside a comprehensive domain research synthesis:
1. **SourceImportCard Structure**: The UI must render a SourceImportCard component with a descriptive summary of bridge seismic retrofit engineering and elastomeric bearing failure analyses containing 3 relevant source items covering AASHTO shear strain criteria, Hanshin forensic reports, and HDRB elastomer aging investigations.
2. **Source Item Metadata**: Each source item in the card must include a clear, descriptive title, a valid URL string, and appropriate source metadata (such as sourceType, sourceName, or summary).
3. **Domain Synthesis Quality**: The accompanying assistant response must synthesize key civil engineering findings integrating coursework concepts with forensic investigation reports, structured with clear technical headings and supported by numbered citations ([1], [2], etc.).""",
    },

    # Case 07
    {
        "name": "case_07_create_artifact",
        "dataset": DATASET,
        "description": "Evaluation case 07: Drafting a rigorous methodological foundation chapter for a multi-criteria decision framework on grid-scale battery storage site selection (1 turns context)",
        "catalog": CATALOG,
        "system_prompt": SYSTEM_PROMPT,
        "messages": [
            {
                "role": "user",
                "content": """Draft a rigorous methodological foundation chapter for a multi-criteria site selection decision framework for grid-scale battery energy storage systems (BESS).
The framework must specify:
1. Mathematical formulation using an additive Multi-Criteria Decision Analysis (MCDA) model combined with TOPSIS (Technique for Order Preference by Similarity to Ideal Solution).
2. Normalization protocols for heterogeneous indicators across discrete cognitive scales (0 to 6).
3. Hierarchical weighting schemes with multi-tiered tie-breaking rules across technical, environmental, and financial dimensions.
4. Systematic literature synthesis of spatial multi-criteria evaluations with full source references.
Please generate the comprehensive chapter alongside an A2UI SourceImportCard indexing the foundational academic references.""",
            },
        ],
        "target": """A valid A2UI payload rendering a SourceImportCard component alongside a comprehensive domain research synthesis:
1. **SourceImportCard Structure**: The UI must render a SourceImportCard component with a descriptive summary of grid-scale battery energy storage site selection methodology containing 6 relevant source items covering spatial MCDA frameworks, TOPSIS algorithms, geocoding substation interconnection models, and environmental hazard screening.
2. **Source Item Metadata**: Each source item in the card must include a clear, descriptive title, a valid URL string, and appropriate source metadata (such as sourceType, sourceName, or summary).
3. **Domain Synthesis Quality**: The accompanying assistant response must deliver a structured methodology chapter including mathematical formulations for additive weighting and TOPSIS distance metrics, discrete scale normalization rules, weighting hierarchies, and literature review with numbered citations ([1], [2], etc.).""",
    },

    # Case 08
    {
        "name": "case_08_researcher",
        "dataset": DATASET,
        "description": "Evaluation case 08: Formulating a multi-phase curriculum study roadmap and laboratory reference guide for quantum key distribution (QKD) optics engineering (2 turns context)",
        "catalog": CATALOG,
        "system_prompt": SYSTEM_PROMPT,
        "messages": [
            {
                "role": "user",
                "content": "We are designing a graduate-level laboratory course on Quantum Key Distribution (QKD) physical layer implementations. What are the key hardware modules required for preparing polarization-encoded BB84 states?",
            },
            {
                "role": "assistant",
                "content": """Setting up a physical-layer polarization-encoded BB84 protocol bench requires five fundamental optical hardware modules [1-5]:

1. **Attenuated Weak Coherent Pulse Source**: 1550 nm distributed feedback (DFB) laser diode with variable optical attenuators (VOAs) calibrated to emit mean photon numbers mu = 0.1 to 0.5 per pulse [1].
2. **State Preparation Polarization Modulator**: Lithium niobate (LiNbO3) phase modulators and motorized quarter/half-wave plates to encode horizontal, vertical, diagonal, and anti-diagonal states [2].
3. **Transmission Channel Simulator**: Spooled single-mode telecom fiber (SMF-28) with controllable polarization controllers and inline variable loss stages simulating 10 to 50 km spans [3].
4. **Active Basis Selection Receiver (Bob)**: Balanced fiber beam splitters, polarizing beam splitter (PBS) cubes, and high-extinction polarization controllers [4].
5. **Single-Photon Detectors**: InGaAs/InP negative feedback avalanche diodes (NFADs) operated in Geiger mode with thermoelectric cooling below -50 deg C and dark count rates < 1 kHz [5].""",
            },
            {
                "role": "user",
                "content": "Please formulate a multi-phase study roadmap and comprehensive technical reference manual covering calibration procedures, quantum bit error rate (QBER) mathematical derivation, and decoy-state security proofs against photon number splitting attacks. Retrieve external literature to compile the reference resources.",
            },
        ],
        "target": """A valid A2UI payload rendering a SourceImportCard component alongside a comprehensive domain research synthesis:
1. **SourceImportCard Structure**: The UI must render a SourceImportCard component with a descriptive summary of Quantum Key Distribution (QKD) physical layer engineering containing 7 relevant source items (1 text report slot plus 6 web sources) covering BB84 protocols, decoy-state security proofs, SPAD detector calibration, and phase randomized coherent sources.
2. **Source Item Metadata**: Each source item in the card must include a clear, descriptive title, a valid URL string, and appropriate source metadata (such as sourceType, sourceName, or summary).
3. **Domain Synthesis Quality**: The accompanying assistant response must deliver a structured multi-phase curriculum roadmap and laboratory reference guide detailing calibration sequences, QBER mathematical models, and decoy-state analysis, supported by numbered citations ([1], [2], etc.).""",
    },

    # Case 09
    {
        "name": "case_09_researcher",
        "dataset": DATASET,
        "description": "Evaluation case 09: Investigating solar astrophysics coronal mass ejection magnetic reconnection dynamics across active and quiescent flux rope states (3 turns context)",
        "catalog": CATALOG,
        "system_prompt": SYSTEM_PROMPT,
        "messages": [
            {
                "role": "user",
                "content": "In solar coronal physics, what characterizes the magnetic flux rope equilibrium prior to a coronal mass ejection (CME) eruption?",
            },
            {
                "role": "assistant",
                "content": """Prior to eruption, a coronal magnetic flux rope is maintained in a quasi-static equilibrium governed by the balance between two competing magnetic forces [1-3]:

* **Outward Magnetic Hoop Force**: Originating from the internal toroidal magnetic field and current within the curved flux rope, driving expansion upward away from the solar surface [1].
* **Inward Strapping Tension Force**: Generated by external overlying potential arcade fields rooted in photospheric magnetic concentrations, providing downward magnetic tension that constrains the rope [2].

Instability occurs when the flux rope ascends to a critical height where the decay index n of the strapping field exceeds approximately 1.5, triggering the Torus Instability [3].""",
            },
            {
                "role": "user",
                "content": "How does the Petschek fast magnetic reconnection mechanism differ from the classic Sweet-Parker model in explaining the rapid energy release during the impulsive phase?",
            },
            {
                "role": "assistant",
                "content": """The primary distinction lies in the geometry of the reconnection diffusion region and the resulting scaling of the reconnection rate with the Lundquist number S [1, 2]:

* **Sweet-Parker Model (1957)**: Features an elongated current sheet of length comparable to the macroscopic system scale L. Because plasma must evacuate through an extremely narrow diffusion layer, the dimensionless reconnection rate scales as S^(-1/2), predicting reconnection timescales on the order of months in the corona—far too slow to explain flare rise times [1].
* **Petschek Fast Reconnection Model (1964)**: Replaces the elongated sheet with a microscopic central diffusion region flanked by pairs of slow-mode magnetohydrodynamic (MHD) shock waves. Most magnetic energy is converted to kinetic and thermal energy across these shocks, yielding a logarithmic scaling rate on the order of 0.01 to 0.1, independent of S, which matches observed flare impulsive timescales [2].""",
            },
            {
                "role": "user",
                "content": "Can you provide recent observational evidence from the Parker Solar Probe and Solar Orbiter regarding turbulent current sheet plasmoid formation during CME reconnection events? Are these in our workspace?",
            },
            {
                "role": "assistant",
                "content": """Our current workspace documents cover classic theoretical MHD formulations up to 2018 but lack in-situ telemetry and coronagraph observations from the Parker Solar Probe (PSP) perihelion encounters and Solar Orbiter's STIX instrument [1].

Would you like me to search external astrophysics databases for recent in-situ measurements of plasmoid-mediated magnetic reconnection in the inner heliosphere?""",
            },
            {
                "role": "user",
                "content": "Yes, please execute the search for recent Parker Solar Probe and Solar Orbiter reconnection findings.",
            },
        ],
        "target": """A valid A2UI payload rendering a SourceImportCard component alongside a comprehensive domain research synthesis:
1. **SourceImportCard Structure**: The UI must render a SourceImportCard component with a descriptive summary of solar coronal mass ejection magnetic reconnection dynamics containing 5 relevant source items covering plasmoid instability, Parker Solar Probe in-situ telemetry, Solar Orbiter observations, and numerical MHD simulations.
2. **Source Item Metadata**: Each source item in the card must include a clear, descriptive title, a valid URL string, and appropriate source metadata (such as sourceType, sourceName, or summary).
3. **Domain Synthesis Quality**: The accompanying assistant response must synthesize key solar astrophysics findings comparing active vs quiescent flux rope states, plasmoid chain formation, and in-situ heliospheric observations, supported by numbered citations ([1], [2], etc.).""",
    },

    # Case 10
    {
        "name": "case_10_researcher",
        "dataset": DATASET,
        "description": "Evaluation case 10: Sourcing standardized semiconductor cleanroom ISO Class 3 electrostatic discharge (ESD) protocols and airborne particle filtration checklists (2 turns context)",
        "catalog": CATALOG,
        "system_prompt": SYSTEM_PROMPT,
        "messages": [
            {
                "role": "user",
                "content": "We are establishing operational protocols for an ISO Class 3 photolithography bay. What are the standardized airborne particulate thresholds per cubic meter according to ISO 14644-1?",
            },
            {
                "role": "assistant",
                "content": """According to **ISO 14644-1:2015 (Cleanrooms and associated controlled environments)**, the cumulative particle concentration thresholds per cubic meter for an **ISO Class 3 cleanroom** are strictly defined as:

* **Particles >= 0.1 micrometers**: Maximum allowable concentration of **1,000 particles/m^3** [1].
* **Particles >= 0.2 micrometers**: Maximum allowable concentration of **237 particles/m^3** [1].
* **Particles >= 0.3 micrometers**: Maximum allowable concentration of **102 particles/m^3** [1].
* **Particles >= 0.5 micrometers**: Maximum allowable concentration of **35 particles/m^3** [1].
* **Particles >= 1.0 micrometers**: Maximum allowable concentration of **8 particles/m^3** [1].
* **Particles >= 5.0 micrometers**: Not permitted / zero detectable limit under ISO Class 3 classification [1].""",
            },
            {
                "role": "user",
                "content": "Please compile a foundational operational checklist covering laminar air velocity standards, ESD wrist-strap continuous ground monitoring (ANSI/ESD S20.20), and gowning air-shower sequencing for fab technicians. Search external cleanroom engineering repositories to verify official industrial specifications.",
            },
        ],
        "target": """A valid A2UI payload rendering a SourceImportCard component alongside a comprehensive domain research synthesis:
1. **SourceImportCard Structure**: The UI must render a SourceImportCard component with a descriptive summary of semiconductor cleanroom ISO Class 3 operational protocols and ESD standards containing 5 relevant source items covering ISO 14644-1 particulate limits, ANSI/ESD S20.20 static control, ULPA filter laminar flow, and cleanroom gowning procedures.
2. **Source Item Metadata**: Each source item in the card must include a clear, descriptive title, a valid URL string, and appropriate source metadata (such as sourceType, sourceName, or summary).
3. **Domain Synthesis Quality**: The accompanying assistant response must deliver a structured operational checklist detailing airflow velocities, electrostatic discharge thresholds, gowning sequencing, and particulate monitoring protocols, supported by numbered citations ([1], [2], etc.).""",
    },
]
