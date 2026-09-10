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

cases = []

# ==============================================================================
# Case 26: Commercial rooftop solar operations & automated cleaning robotics
# B2B sales enablement value proposition (4 slots in SourceImportCard; 5 messages / 3 turns context)
# ==============================================================================
cases.append({
    "name": "case_26_researcher",
    "dataset": DATASET,
    "description": "Evaluation case 26: Formulating B2B value proposition frameworks and sales enablement methodologies for commercial rooftop solar automated cleaning robotics O&M services (3 turns context)",
    "catalog": CATALOG,
    "system_prompt": SYSTEM_PROMPT,
    "messages": [
        {
            "role": "user",
            "content": "Could you recommend frameworks to help structure our B2B commercialization and sales enablement strategy for commercial rooftop solar operations and automated cleaning robotics?",
        },
        {
            "role": "assistant",
            "content": """Commercializing automated robotic cleaning and predictive operations & maintenance (O&M) for commercial & industrial (C&I) rooftop solar portfolios requires bridging upfront robotics adoption costs with long-term levelized cost of energy (LCOE) gains [1]:

To tailor the most effective sales enablement strategy and collateral, which direction would you prefer to prioritize?

1. **Strategic Commercialization Focus**:
   * **Value Proposition & Financial ROI**: Levelized cost of energy (LCOE) modeling, soiling ratio recovery yield benchmarks, and performance-ratio warranty structures.
   * **Robotics Deployment & Contracting**: Dry vs wet robotic cleaning operational specifications, roof load compliance, and long-term O&M service level agreements (SLAs).
2. **Collateral & Sales Enablement Format**:
   * **Consultative Pitch Playbook**: Hypothesis-driven pitch deck structures, customer objection-handling scripts, and discovery questions for building asset managers.
   * **Technical Dossier**: Engineering whitepapers on photovoltaic soiling degradation curves and optical loss calculations.

Please let me know your preferred focus, and I will structure our research roadmap accordingly.""",
        },
        {
            "role": "user",
            "content": "Let's focus on the value proposition and financial ROI models for C&I rooftop solar robotic cleaning, along with consultative sales enablement frameworks for property asset managers.",
        },
        {
            "role": "assistant",
            "content": """Target confirmed: **C&I Rooftop Solar Cleaning Robotics B2B Value Proposition & Sales Enablement** [1-3].

Based on solar asset management literature, here is an initial synthesis across three core pillars:
1. **Photovoltaic Soiling Degradation & Yield Loss**: Atmospheric dust, particulate matter, and bird droppings cause 4% to 12% annualized yield degradation in high-dust commercial corridors, escalating to >25% in agricultural or arid regions [1].
2. **Automated Cleaning Robotics vs Manual Washing**: Lightweight, waterless track-based or autonomous crawler robots eliminate manual rooftop labor hazards, protect fragile solar glass coatings, and reduce water consumption to near zero [2].
3. **Value-Based O&M Service Contracts**: Shifting commercial proposals from transactional cleaning fees to performance-guaranteed service agreements where robotics costs are amortized against verified kilowatt-hour yield recovery [3].

Our current workspace contains general solar equipment catalogs but lacks verified multi-year soiling recovery financial models and consultative sales objection-handling playbooks [1]. Would you like me to conduct an external technical and commercial literature search?""",
        },
        {
            "role": "user",
            "content": "Yes, please search the web for commercial rooftop solar automated cleaning robotics ROI models, soiling yield recovery data, and B2B consultative sales enablement frameworks.",
        },
    ],
    "target": """A valid A2UI payload rendering a SourceImportCard component alongside a comprehensive domain research synthesis:
1. **SourceImportCard Structure**: The UI must render a SourceImportCard component with a descriptive summary of commercial rooftop solar cleaning robotics and B2B sales enablement value propositions containing 4 relevant source items covering photovoltaic soiling loss degradation models, automated cleaning robotics ROI, performance-guaranteed O&M service contracts, and consultative sales presentation frameworks.
2. **Source Item Metadata**: Each source item in the card must include a clear, descriptive title, a valid URL string, and appropriate source metadata (such as sourceType, sourceName, or summary).
3. **Domain Synthesis Quality**: The accompanying assistant response must synthesize key findings addressing the user's research request regarding commercial rooftop solar robotic cleaning value propositions, structured with clear headings/bullet points (equivalent section/heading structures like Pillars, Sections, or Value Drivers are acceptable), incorporating relevant domain concepts (such as levelized cost of energy [LCOE], soiling ratio [SR], waterless cleaning robotics, and performance-ratio warranties), and supported by numbered citations ([1], [2], etc.).""",
})

# ==============================================================================
# Case 27: Management consulting whitespaces in regional community banking core-banking cloud modernization
# (6 slots in SourceImportCard; 5 messages / 3 turns context)
# ==============================================================================
cases.append({
    "name": "case_27_researcher",
    "dataset": DATASET,
    "description": "Evaluation case 27: Identifying management consulting market whitespaces and regulatory compliance frameworks for regional community banking core-banking cloud modernization (3 turns context)",
    "catalog": CATALOG,
    "system_prompt": SYSTEM_PROMPT,
    "messages": [
        {
            "role": "user",
            "content": "I want to explore high-value management consulting market whitespaces in regional community banking core-banking cloud modernization.",
        },
        {
            "role": "assistant",
            "content": """Regional community banks ($500M to $10B in assets) face severe digital transformation bottlenecks driven by legacy core provider dependencies and accelerating fintech competition [1-4]:

* **Legacy Mainframe Oligopoly vs Next-Gen Cores**: Over 80% of community banks rely on monolithic legacy cores (e.g. FIS, Fiserv, Jack Henry) with multi-year restrictive contracts, creating high friction for migrating to cloud-native platforms (e.g. Thought Machine, Mambu, nCino) [1].
* **Composable Banking & API Modernization**: Transitioning to microservices-based architectures and headless core APIs enables modular product rollouts without high-risk rip-and-replace core overhauls [2].
* **Regulatory Compliance & FFIEC Cloud Guardrails**: Navigating strict FDIC, OCC, and Federal Reserve supervisory expectations under the FFIEC Architecture, Infrastructure, and Operations (AIO) Examination Handbook regarding third-party cloud concentration risk [3].
* **Core Modernization Business Case & Deposit Preservation**: Defending commercial deposit franchises and lowering cost-to-income ratios while mitigating core conversion operational outage risks [4].

Shall we focus our consulting whitespace analysis on regulatory compliance and vendor risk management, or on migration delivery playbooks and commercial monetization frameworks?""",
        },
        {
            "role": "user",
            "content": "Let's investigate regulatory compliance under FFIEC cloud architecture standards, core migration cutover risk mitigation, and advisory playbooks for community bank boards.",
        },
        {
            "role": "assistant",
            "content": """Our workspace contains general fintech market overviews but lacks detailed regulatory compliance guidelines from the FFIEC Information Technology Examination Handbook and empirical core banking migration cutover risk playbooks [1].

I can execute an external search across banking regulatory agency bulletins (FDIC, OCC, Fed), bank technology consultancy whitepapers, and core banking contract restructuring benchmarks to map out high-value advisory service offerings. Would you like me to initiate this research?""",
        },
        {
            "role": "user",
            "content": "Please research regional community banking core-banking cloud modernization whitespaces, FFIEC regulatory guardrails, and migration advisory frameworks to help design our consulting practice.",
        },
    ],
    "target": """A valid A2UI payload rendering a SourceImportCard component alongside a comprehensive domain research synthesis:
1. **SourceImportCard Structure**: The UI must render a SourceImportCard component with a descriptive summary of regional community banking core-banking cloud modernization containing 6 relevant source items covering legacy core migration risks, cloud-native core platforms, FFIEC regulatory compliance guardrails, core contract renegotiations, parallel-run testing methodologies, and high-value consulting advisory service packs.
2. **Source Item Metadata**: Each source item in the card must include a clear, descriptive title, a valid URL string, and appropriate source metadata (such as sourceType, sourceName, or summary).
3. **Domain Synthesis Quality**: The accompanying assistant response must deliver a structured management consulting analysis outlining high-value advisory whitespaces, regulatory compliance requirements (FFIEC, FDIC, OCC), core conversion cutover strategies, and modernization economic models, supported by numbered citations ([1], [2], etc.).""",
})

# ==============================================================================
# Case 28: Biographical documentary audio script outline on early deep-sea
# bathysphere pioneer William Beebe and Otis Barton (3 slots in SourceImportCard; 1 message / 1 turn context)
# ==============================================================================
cases.append({
    "name": "case_28_researcher",
    "dataset": DATASET,
    "description": "Evaluation case 28: Developing a detailed multi-act narrative script outline for a biographical documentary on deep-sea bathysphere pioneers William Beebe and Otis Barton (1 turns context)",
    "catalog": CATALOG,
    "system_prompt": SYSTEM_PROMPT,
    "messages": [
        {
            "role": "user",
            "content": """I am preparing a long-form audio documentary script about early deep-sea bathysphere pioneers William Beebe and Otis Barton and their historic 1930–1934 Bermuda descents into the ocean's bathypelagic abyss.
Please outline an accessible, multi-act narrative treatment for audio listeners without technical jargon:
* Act I: The Hollow Steel Sphere — Otis Barton's radical cast-steel engineering design, fused quartz portholes, and the partnership with famed naturalist William Beebe off Nonsuch Island.
* Act II: Into the Twilight Zone — The harrowing 1930 uncrewed test dips, electrical phone line communications with Gloria Hollister aboard the support barge Ready, and descending beyond sunlight at 800 feet.
* Act III: Living in the Half Mile Down — The record-shattering 1934 dive to 3,028 feet (half a mile), encountering bioluminescent deep-sea siphonophores and lanternfish, and battling suffocating carbon dioxide.
* Act IV: Legacy of Deep-Sea Exploration — The transition from static tethered spheres to modern autonomous submersibles and Beebe's popularization of marine ecology.
Incorporate primary logbook quotes, sensory descriptions of cold condensation inside the sphere, and compile an A2UI SourceImportCard indexing authoritative archival and oceanographic museum sources.""",
        },
    ],
    "target": """A valid A2UI payload rendering a SourceImportCard component alongside a comprehensive domain research synthesis:
1. **SourceImportCard Structure**: The UI must render a SourceImportCard component with a descriptive summary of William Beebe and Otis Barton's bathysphere deep-sea expeditions containing 3 relevant source items covering New York Zoological Society historical archives, William Beebe's expedition accounts (Half Mile Down), and technical engineering records of Otis Barton's bathysphere design.
2. **Source Item Metadata**: Each source item in the card must include a clear, descriptive title, a valid URL string, and appropriate source metadata (such as sourceType, sourceName, or summary).
3. **Domain Synthesis Quality**: The accompanying assistant response must deliver a compelling, multi-act biographical documentary narrative script outline detailing the bathysphere's mechanical innovations (cast-steel hull, fused quartz windows, telephone comms), underwater ecological observations, primary archival quotes, and the legacy of bathypelagic exploration, supported by numbered citations ([1], [2], etc.).""",
})

# ==============================================================================
# Case 29: Plant circadian rhythm clock genes, phytochrome photoreceptors, and
# photoperiodic flowering induction (5 slots in SourceImportCard; 5 messages / 3 turns context)
# ==============================================================================
cases.append({
    "name": "case_29_researcher",
    "dataset": DATASET,
    "description": "Evaluation case 29: Exploring molecular mechanisms of plant circadian clock genes, phytochrome photoreceptors, and photoperiodic flowering induction (3 turns context)",
    "catalog": CATALOG,
    "system_prompt": SYSTEM_PROMPT,
    "messages": [
        {
            "role": "user",
            "content": "Discuss plant circadian clock mechanisms and photoperiodic flowering based on our uploaded references.",
        },
        {
            "role": "assistant",
            "content": """Based on plant physiology and molecular biology literature, the plant circadian system coordinates daily biological rhythms and photoperiodic transitions through three interconnected regulatory axes [1-3]:

### 1. The Central Core Oscillator Feedback Loops
* At dawn, the MYB-domain transcription factors **CIRCADIAN CLOCK ASSOCIATED 1 (CCA1)** and **LATE ELONGATED HYPOCOTYL (LHY)** peak, directly binding the evening element (EE) in the promoter of **TIMING OF CAB EXPRESSION 1 (TOC1 / PRR1)** to repress evening gene expression [1].
* Throughout the day, PSEUDO-RESPONSE REGULATOR proteins (PRR9, PRR7, PRR5) sequentially repress CCA1 and LHY, allowing TOC1 and the Evening Complex (ELF3-ELF4-LUX) to activate evening transcription before dawn resets the cycle [1].

### 2. Photoreceptor Light Signaling & Entrainment
* Phytochromes (**phyA through phyE**) detect red and far-red light via reversible photoconversion between the inactive Pr and biologically active Pfr conformers [2].
* Cryptochromes (cry1, cry2) perceive blue and UVA photons, directly modulating clock protein turnover and entraining the central oscillator to diurnal solar cycles [2].

### 3. Photoperiodic Floral Transition & Systemic Florigen Signaling
* Under inductive long-day conditions, circadian-regulated transcription of **CONSTANS (CO)** in leaf phloem companion cells triggers the expression of **FLOWERING LOCUS T (FT)**, the mobile florigen protein that translocates through sieve tubes to the shoot apical meristem to induce flowering [3].

Would you like me to conduct a targeted molecular literature search to explore specific post-translational protein interactions or epigenetic gating mechanisms?""",
        },
        {
            "role": "user",
            "content": "How do phytochrome B and E3 ubiquitin ligase complexes regulate CONSTANS protein stability during long-day photoperiodic flowering induction?",
        },
        {
            "role": "assistant",
            "content": """The current workspace contains foundational textbook summaries of plant physiology but lacks detailed molecular papers on the post-translational regulation of CONSTANS (CO) protein kinetics, particularly regarding the **CONSTITUTIVE PHOTOMORPHOGENIC 1 / SUPPRESSOR OF PHYA-105 (COP1/SPA)** E3 ubiquitin ligase complex and phytochrome B (phyB) versus phytochrome A (phyA) antagonist phosphorylation dynamics [1].

I can execute a specialized technical literature search across plant molecular genetics repositories for recent empirical studies on the ubiquitin-proteasome degradation of CO, blue-light cryptochrome stabilization (via FKF1), and phloem-specific FT transcriptional activation. Would you like me to proceed with this search?""",
        },
        {
            "role": "user",
            "content": "Yes, please search the plant molecular biology literature for phytochrome regulation of CONSTANS protein stability, COP1/SPA ubiquitin ligase kinetics, and photoperiodic FT flowering induction.",
        },
    ],
    "target": """A valid A2UI payload rendering a SourceImportCard component alongside a comprehensive domain research synthesis:
1. **SourceImportCard Structure**: The UI must render a SourceImportCard component with a descriptive summary of plant circadian clock genes, phytochromes, and photoperiodic flowering induction containing 5 relevant source items covering central oscillator feedback loops (CCA1/LHY and TOC1), phytochrome photoreceptors (phyA and phyB), CONSTANS (CO) transcriptional and post-translational regulation, FLOWERING LOCUS T (FT) florigen signaling, and circadian gating of environmental responses.
2. **Source Item Metadata**: Each source item in the card must include a clear, descriptive title, a valid URL string, and appropriate source metadata (such as sourceType, sourceName, or summary).
3. **Domain Synthesis Quality**: The accompanying assistant response must deliver a structured botanical and molecular synthesis detailing core transcriptional-translational feedback loops (TTFL), red/far-red light photoreversibility, florigen phloem transport, and photoperiodic inductive mechanisms, supported by numbered citations ([1], [2], etc.).""",
})

# ==============================================================================
# Case 30: Undergraduate senior thesis on urban rails-to-trails greenway conversions
# & pedestrian accessibility (35 messages / 18 turns context; 5 slots in SourceImportCard)
# ==============================================================================
c30_msgs = []
topics_c30 = [
    (
        "Sorry, I uploaded the wrong project document! I am an undergraduate student starting my senior thesis on urban rails-to-trails conversions and pedestrian accessibility.",
        "No worries! Let's clear the slate. Urban rails-to-trails conversions represent a fantastic, multidisciplinary thesis topic bridging transportation planning, landscape architecture, GIS spatial analysis, and public health [1]. What city, abandoned rail corridor, or geographic community is your thesis focusing on?",
    ),
    (
        "I am focusing on the transformation of abandoned industrial rail spurs into continuous multi-use urban greenways, examining the High Line and Atlanta BeltLine as comparative benchmarks.",
        "The High Line in New York City and the Atlanta BeltLine are seminal, contrasting benchmarks in urban rail conversions [1-2]. The High Line exemplifies elevated park linear revitalization and high-density tourist activation [1], while the 22-mile Atlanta BeltLine loop emphasizes equitable transit connectivity, multi-neighborhood active mobility, and industrial brownfield remediation [2].",
    ),
    (
        "What are the recommended trail cross-section widths and lane separations for high-volume urban greenways?",
        "According to AASHTO and Rails-to-Trails Conservancy guidelines, high-volume urban multi-use paths should feature a minimum 12-foot (3.6 m) paved asphalt or concrete surface, ideally expanding to 14–16 feet with 2-foot graded soft-surface shoulders [3]. In congested segments, separating a 10-foot two-way bicycle track from an adjacent 6-foot pedestrian walkway prevents high-speed conflict [3].",
    ),
    (
        "How do grade-separated crossings over arterial roadways impact structural costs versus at-grade signalized mid-block crossings?",
        "Grade-separated prefabricated steel truss pedestrian bridges cost $2M to $5M due to deep structural abutment foundations and ADA-compliant ramp switchbacks [4]. Conversely, at-grade mid-block crossings with Pedestrian Hybrid Beacons (HAWK signals), high-visibility continental crosswalk striping, and curb bulb-outs cost $50,000 to $150,000 while maintaining acceptable safety thresholds [4].",
    ),
    (
        "What are the standard ADA maximum slope and cross-slope guidelines for paved greenway multi-use paths?",
        "Under the Public Rights-of-Way Accessibility Guidelines (PROWAG), the continuous running slope of a multi-use path should not exceed 5% (1:20) [5]. Where terrain necessitates steeper grades up to 8.33% (1:12), level resting landings must be provided every 30 feet, and transverse cross-slopes must remain strictly capped at 2% for stormwater runoff without overturning wheelchairs [5].",
    ),
    (
        "How should I measure pedestrian and cyclist level of traffic stress (LTS) at greenway access portals?",
        "Apply the Mekuria Level of Traffic Stress (LTS 1 through 4) framework to all connector roadways leading to trailheads [6]. LTS 1 reflects low-speed, low-volume residential streets suitable for all ages, while multi-lane arterial feeders without physical barrier protection rate as LTS 3 or 4, indicating high stress that physically severs adjoining neighborhoods from trail portals [6].",
    ),
    (
        "What environmental soil remediation techniques are required for converting contaminated industrial rail corridors?",
        "Rail rights-of-way typically contain polycyclic aromatic hydrocarbons (PAHs) from creosote-treated ties, arsenic, and heavy metals [7]. Standard remedial encapsulation places a non-woven geotextile marker fabric barrier over contaminated subgrade, capped by 12 to 18 inches of certified clean fill soil along landscaped verges and sealed asphalt over the trail prism [7].",
    ),
    (
        "How can greenway design prevent 'green gentrification' and displacement of long-time lower-income residents?",
        "Mitigating green gentrification requires pairing physical infrastructure with proactive equitable development policies [8]: establishing Community Land Trusts (CLTs) along the corridor, adopting inclusionary zoning overlays requiring affordable housing set-asides, enacting property tax freeze programs for legacy homeowners, and supporting neighborhood business incubators at trailheads [8].",
    ),
    (
        "What GIS spatial network analysis methods should I use to calculate 10-minute pedestrian catchment areas around trail access points?",
        "Use the ArcGIS Service Area Network Analysis tool with topologically structured pedestrian walkways rather than simple planar Euclidean buffers [9]. Parameterize walking impedance at a standard pedestrian velocity of 1.2 m/s (3 mph), factoring in intersection signal delays and terrain slope to generate realistic 800-meter (0.5-mile) 10-minute walksheds [9].",
    ),
    (
        "How do permeable pavement surfaces compare to standard asphalt for stormwater runoff volume reduction?",
        "Porous asphalt, pervious concrete, and permeable interlocking pavers reduce peak stormwater runoff volume by 70% to 90% and filter suspended solids into aggregate sub-base recharge beds [10]. However, they require twice-yearly regenerative-air vacuum sweeping to prevent fine sediment clogging and have lower freeze-thaw durability than dense-graded hot-mix asphalt [10].",
    ),
    (
        "What lighting standards and CPTED principles should be integrated for nocturnal trail safety without disturbing urban wildlife?",
        "Incorporate Crime Prevention Through Environmental Design (CPTED) by maintaining clear sightlines—pruning shrubs below 3 feet and tree branches above 7 feet [11]. Pair this with full-cutoff 3000K warm LED luminaires delivering 0.5 to 1.0 foot-candles average illuminance, utilizing passive infrared motion dimmers to minimize nocturnal light pollution in ecological zones [11].",
    ),
    (
        "How should I structure the methodology chapter of my undergraduate senior thesis?",
        "Structure the methodology across four rigorous empirical phases [12]: (1) Spatial GIS Pedestrian Network Walkshed Modeling; (2) Microclimate Thermal Sensor Mapping and NDVI Canopy Assessment; (3) Multi-Modal Trail User Intercept Surveys and Infrared Automated Volume Counts; (4) Difference-in-Differences Hedonic Property Valuation Analysis [12].",
    ),
    (
        "What automated counting technologies are best for monitoring trail volume: infrared pyroelectric sensors or inductive loop counters?",
        "The gold standard is a combined sensor array [13]. Passive infrared pyroelectric sensors (e.g. Eco-Counter) detect the thermal differential of all passing bodies, while in-pavement electromagnetic inductive loops detect bicycle wheel metallic disturbances, allowing automated classification and directional tallying of pedestrians versus cyclists [13].",
    ),
    (
        "What hedonic price regression model specifications capture the economic impact on property values near trailheads?",
        "Specify a semi-logarithmic difference-in-differences (DiD) hedonic regression model [14]: ln(Price_it) = alpha + beta_1(Post_t * NearTrail_i) + gamma X_it + delta_t + eta_i + epsilon_it. Define discrete distance buffer rings (0–200m, 200–500m, 500–1000m) to measure price appreciation gradients while controlling for structural dwelling attributes and census tract fixed effects [14].",
    ),
    (
        "What are typical maintenance costs per mile per year for urban paved greenways?",
        "Annual municipal operating expenditures for paved urban rail-trails typically range from $7,000 to $14,000 per mile [15]. Budget line items include weekly trash collection, bi-monthly mowing and brush clearing, annual crack sealing and pavement marking, hazard tree pruning, graffiti abatement, and lighting repairs [15].",
    ),
    (
        "How can native pollinator meadows and bioswales be designed along the trail verges?",
        "Bioswales with deep engineered sandy loam filtration beds capture trail runoff, planted with drought-tolerant native perennials and pollinator species (e.g. Asclepias tuberosa, Echinacea purpurea, Bouteloua gracilis) [16]. This turns linear rights-of-way into contiguous biological pollinator highways while reducing municipal mowing expenditures [16].",
    ),
    (
        "Can we search for recent 2022–2025 empirical peer-reviewed studies on green gentrification, urban heat island mitigation, and micromobility modal shifts on converted rail trails?",
        "The current workspace contains foundational trail planning guidelines up to 2020 but lacks recent 2022–2025 published empirical papers examining e-bike/e-scooter micromobility adoption rates, satellite microclimate cooling measurements along greenway corridors, and anti-displacement zoning evaluations [1]. Would you like me to search external academic repositories for these recent empirical studies?",
    ),
]

for q, a in topics_c30:
    c30_msgs.append({"role": "user", "content": q})
    c30_msgs.append({"role": "assistant", "content": a})

c30_msgs.append({
    "role": "user",
    "content": "Yes, please search the urban planning and transportation literature for recent empirical studies on rail-trail greenway conversions, pedestrian accessibility metrics, and green gentrification mitigation to ground my thesis.",
})

cases.append({
    "name": "case_30_researcher",
    "dataset": DATASET,
    "description": "Evaluation case 30: Guiding an undergraduate graduation thesis research workflow on urban rails-to-trails greenway conversions and pedestrian accessibility (18 turns context)",
    "catalog": CATALOG,
    "system_prompt": SYSTEM_PROMPT,
    "messages": c30_msgs,
    "target": """A valid A2UI payload rendering a SourceImportCard component alongside a comprehensive domain research synthesis:
1. **SourceImportCard Structure**: The UI must render a SourceImportCard component with a descriptive summary of urban rails-to-trails greenway conversions and pedestrian accessibility containing 5 relevant source items covering trail geometric design standards (AASHTO / Rails-to-Trails Conservancy), GIS walkshed network accessibility, green gentrification and housing affordability impacts, urban microclimate cooling, and micromobility integration.
2. **Source Item Metadata**: Each source item in the card must include a clear, descriptive title, a valid URL string, and appropriate source metadata (such as sourceType, sourceName, or summary).
3. **Domain Synthesis Quality**: The accompanying assistant response must deliver a structured academic thesis literature review covering trail design geometry, Level of Traffic Stress (LTS) portal connectivity, hedonic pricing and displacement mitigation, and empirical post-2022 modal shift datasets, supported by numbered citations ([1], [2], etc.).""",
})


class IndentedDumper(yaml.SafeDumper):
    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)


def str_presenter(dumper, data):
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


IndentedDumper.add_representer(str, str_presenter)

# Schema validation
with open("eval/datasets/dataset_schema.json", "r", encoding="utf-8") as f:
    schema = json.load(f)

jsonschema.validate(instance=cases, schema=schema)
print("Schema validation PASSED!")

out_path = Path("temp_docs/batch_6.yaml")
with open(out_path, "w", encoding="utf-8") as f:
    yaml.dump(cases, f, Dumper=IndentedDumper, sort_keys=False, width=1000)

print(f"Successfully generated {out_path} ({out_path.stat().st_size} bytes)")
