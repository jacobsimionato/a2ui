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

"""Generator for calibrated Cases 11 to 15 (batch_3.yaml)."""

import json
import yaml
import jsonschema

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
# Case 11: Hollywood blockbuster actor compensation & profit-sharing
# (Tom Cruise Top Gun: Maverick upfront fee, backend points, box office milestones;
# 4 slots in SourceImportCard; 3 messages / 2 turns context)
# ==============================================================================
cases.append({
    "name": "case_11_researcher",
    "dataset": DATASET,
    "description": "Evaluation case 11: Gathering public financial and contractual compensation metrics across Hollywood blockbuster actor profit-sharing agreements (2 turns context)",
    "catalog": CATALOG,
    "system_prompt": SYSTEM_PROMPT,
    "messages": [
        {
            "role": "user",
            "content": "What was Tom Cruise's contracted compensation and profit-sharing structure for Top Gun: Maverick, specifically his upfront fee, first-dollar gross backend points, and box office milestone escalators?",
        },
        {
            "role": "assistant",
            "content": """Based on entertainment industry trade disclosures and studio reporting, Tom Cruise's compensation package for *Top Gun: Maverick* was structured around a high-leverage profit-participation agreement rather than a standard flat salary [1–3]:

* **Upfront Base Salary**: Cruise accepted an initial upfront fee of approximately $12.5M to $13M, keeping upfront production overhead lower in exchange for extensive downstream profit participation [1].
* **First-Dollar Gross (FDG) Backend Points**: The agreement granted an estimated 10% first-dollar gross backend cut, entitling him to a percentage of studio gross revenues from the opening day of release before standard studio overhead deductions [2].
* **Box Office Milestone Escalators & Total Payout**: Milestone bonuses triggered as global theatrical box office surpassed $500M, $1.0B, and ultimately $1.49B worldwide, pushing his total compensation past $100M–$110M when combined with subsequent premium video-on-demand (PVOD) and streaming home entertainment revenues [3].

Would you like me to search entertainment business and box office trade repositories for verified contract metrics, comparable superstar backend packages, and studio profit-sharing structures?""",
        },
        {
            "role": "user",
            "content": "Yes, please search entertainment business and trade databases for verified contract metrics, upfront base fees, first-dollar gross backend profit participation points, and box office milestone escalation clauses for major Hollywood blockbuster star deals.",
        },
    ],
    "target": """A valid A2UI payload rendering a SourceImportCard component alongside a comprehensive domain research synthesis:
1. **SourceImportCard Structure**: The UI must render a SourceImportCard component with a descriptive summary of Hollywood blockbuster actor compensation and profit-sharing contracts containing 4 relevant source items covering upfront talent fees, first-dollar gross backend participation, box office milestone escalators, and studio profit accounting metrics.
2. **Source Item Metadata**: Each source item in the card must include a clear, descriptive title, a valid URL string, and appropriate source metadata (such as sourceType, sourceName, or summary).
3. **Domain Synthesis Quality**: The accompanying assistant response must synthesize key entertainment business and talent compensation findings comparing upfront salaries against backend gross participation structures and box office milestone tiers, supported by numbered citations ([1], [2], etc.).""",
})


# ==============================================================================
# Case 12: Digital music streaming & copyright infringement lawsuit procedural analysis
# (statutory fair use claims, royalty damages, regional appellate rulings;
# 4 slots in SourceImportCard; 5 messages / 3 turns context)
# ==============================================================================
cases.append({
    "name": "case_12_researcher",
    "dataset": DATASET,
    "description": "Evaluation case 12: Performing multi-angle legal intelligence analysis of an active digital music streaming copyright infringement lawsuit (3 turns context)",
    "catalog": CATALOG,
    "system_prompt": SYSTEM_PROMPT,
    "messages": [
        {
            "role": "user",
            "content": "Please provide a structured 5-part procedural analysis of the active digital music streaming copyright infringement lawsuit (Case No. 2026-CV-44190, SoundWave Publishing Ltd. v. StreamVibe Media & Algorithmic Audio Networks Inc.) based on submitted case filings and attached exhibits. The analysis must cover: (1) Plaintiff claims and legal theories regarding unlicensed mechanical reproductions and statutory damages, (2) Defendant preliminary defenses asserting DMCA Section 512 safe harbor and transformative fair use, (3) Current procedural timeline and status, (4) Case management orders and paradigm decisions, and (5) A structured convergence and divergence matrix comparing both parties' positions. Please provide precise citations to document pages and report any unviewed pages.",
        },
        {
            "role": "assistant",
            "content": """Here is the structured 5-part procedural analysis of **Case No. 2026-CV-44190** (*SoundWave Publishing Ltd. v. StreamVibe Media & Algorithmic Audio Networks Inc.*) based on submitted case filings [1–48]:

---

### 1. Plaintiff Claims, Legal Theories & Quantum of Damages
* **Core Grievance**: Unlicensed mechanical reproduction, ingestion, and server-side distribution of 14,200 catalog musical compositions for streaming recommendation models and synthetic audio stem extraction without obtaining Section 115 mechanical compulsory licenses or paying standard statutory mechanical royalty rates [1–4].
* **Substantive Legal Theories**:
  * *Direct & Contributory Copyright Infringement*: Violations of exclusive reproduction (§ 106(1)) and distribution (§ 106(3)) rights under the Copyright Act of 1976 [5–8].
  * *Willful Infringement*: Bypassing Mechanical Licensing Collective (MLC) notice-of-intention procedures to expedite catalog onboarding [9, 10].
* **Monetary Prayer**: Maximum statutory damages under 17 U.S.C. § 504(c)(2) ($150,000 per infringed work, potentially exceeding $2.1B), disgorgement of subscription advertising profits, and permanent injunctive relief [11–14].

---

### 2. Defendant Preliminary Objections & Affirmative Defenses
* **DMCA Section 512(c) Safe Harbor Immunity**: StreamVibe asserts safe harbor protections, contending audio tracks were uploaded by licensed distributor feeds and cached automatically without actual or red-flag knowledge of ownership conflicts, coupled with prompt response to takedown notices [15–18].
* **Transformative Fair Use (§ 107)**: Defendants argue algorithmic audio feature vectorization, latent acoustic indexing, and internal mathematical feature mapping constitute highly transformative non-expressive intermediate use [19–22].
* **Implied License & Industry Acquiescence**: Contending SoundWave accepted blanket streaming revenue disbursements during initial catalog rollout [23–25].

---

### 3. Procedural Timeline & Current Litigation Status
* **January 15, 2026**: Initial Complaint and emergency motion for preliminary injunction filed in District Court [26, 27].
* **February 28, 2026**: Preliminary injunction denied; court found no showing of irreparable harm given calculable statutory royalty remedies [28, 29].
* **April 14, 2026**: Defendant filed formal Answer and Affirmative Defenses with 6 technical exhibits [30–33].
* **May 20, 2026**: Magistrate judge presided over settlement conference; negotiations stalled over mechanical royalty valuation [34, 35].
* **Current Status**: Proceeding to expert evidentiary discovery on server ingestion logs and audio feature vectors [36].

---

### 4. Interlocutory Orders & Attached Precedents
* **Interlocutory Order No. 03**: Presiding judge ordered preservation of raw machine-learning ingestion pipelines and intermediate cached audio files [37, 38].
* **Attached Defense Exhibits**: Defendant attached three out-of-circuit district rulings treating algorithmic indexing and intermediate cached data as non-infringing fair use [39–42].

---

### 5. Convergence & Divergence Matrix

| Analytical Issue | Plaintiff Position (SoundWave) | Defendant Position (StreamVibe) | Evidentiary Basis |
| :--- | :--- | :--- | :--- |
| **Mechanical Licensing** | Direct infringement for failure to secure § 115 compulsory licenses [43] | Stream caching exempt from mechanical reproduction requirements under service agreements [44] | Ingestion Protocol Logs (Ex. B) |
| **DMCA Safe Harbor** | Inapplicable to platform-initiated algorithmic vectorization and catalog exploitation [45] | Complete defense under § 512(c) as automated technical storage [46] | Terms of Service & Feed Records (Ex. D) |
| **Fair Use (§ 107)** | Non-transformative commercial reproduction substituting for licensed works [47] | Transformative intermediate utility establishing mathematical audio vectors [48] | Technical Architecture Affidavit (Ex. F) |

*Note: All 118 submitted pages have been fully reviewed with zero unviewed pages.*

⚖️ Would you like me to research regional appellate court precedents in this circuit regarding platform mechanical reproduction liability and statutory fair use boundaries?""",
        },
        {
            "role": "user",
            "content": "What is the current decision trend of regional appellate panels regarding whether computational vectorization and streaming caching qualify for statutory fair use or DMCA safe harbor immunity?",
        },
        {
            "role": "assistant",
            "content": """**The case records currently in your workspace do not contain regional appellate decisions from this specific judicial circuit.**

The filings submitted by the defense rely entirely on out-of-circuit persuasive authority and trial-level rulings [1–4]:
* *Second Circuit Precedents*: Applying rigorous commercial scrutiny where intermediate digital copies displace or substitute licensed music distribution channels [1, 2].
* *Ninth Circuit Precedents*: Distinguishing between nominative search indexing versus proprietary computational exploitation of expressive audio works [3, 4].

**Would you like me to perform an external search across regional appellate court repositories to identify binding circuit jurisprudence regarding digital streaming mechanical royalty damages, transformative fair use, and DMCA safe harbor thresholds?**""",
        },
        {
            "role": "user",
            "content": "Yes, please search external legal databases for regional appellate court rulings and statutory fair use interpretations regarding digital streaming royalty damages.",
        },
    ],
    "target": """A valid A2UI payload rendering a SourceImportCard component alongside a comprehensive domain research synthesis:
1. **SourceImportCard Structure**: The UI must render a SourceImportCard component with a descriptive summary of digital music streaming copyright litigation and mechanical royalty liability containing 4 relevant source items covering statutory fair use jurisprudence, DMCA Section 512 safe harbor limits, mechanical compulsory licensing damages, and regional appellate copyright precedents.
2. **Source Item Metadata**: Each source item in the card must include a clear, descriptive title, a valid URL string, and appropriate source metadata (such as sourceType, sourceName, or summary).
3. **Domain Synthesis Quality**: The accompanying assistant response must synthesize key legal findings addressing digital streaming copyright infringement, statutory royalty damages under Section 504, transformative use defenses, and appellate circuit standards, supported by numbered citations ([1], [2], etc.).""",
})


# ==============================================================================
# Case 13: High-vacuum orbital satellite environmental test chamber (TVAC)
# cryogenic shroud control & thermal stabilization consultation
# (63 messages / 32 turns context; 5 slots in SourceImportCard)
# ==============================================================================
c13_msgs = []
topics_c13 = [
    (
        "Cryogenic shroud Zone 1-4 liquid nitrogen (LN2) flooded mode boiling transition during rapid chill-down to 80 K shows pressure oscillations in supply manifold line A.",
        "Analysis of the cryogenic feed telemetry indicates an unstable film boiling to nucleate boiling transition at the copper shroud tube wall, generating localized vapor choking and pressure swings of 0.35 bar(g) [1, 2]. Operating subcooled liquid nitrogen at 1.8 bar(g) suppresses vapor slug formation during the transient chill-down phase [1, 3]."
    ),
    (
        "Quartz crystal microbalance (QCM) outgassing deposition rate at -20 deg C shroud background during chamber pump-down below 1e-6 Torr.",
        "The cryogenic QCM sensor telemetry confirms condensable molecular deposition has stabilized at 0.85 ng/cm^2/hr at -20 deg C, which satisfies the ECSS outgassing threshold of < 1.0 ng/cm^2/hr prior to activating payload electronics [4, 5]."
    ),
    (
        "Shroud thermal gradient uniformity across cylindrical barrel vs end-dome cryo-panels under 15 kW radiative bus dissipation.",
        "Thermal survey data from 36 platinum RTDs indicates a maximum shroud surface temperature gradient of 2.3 K across the cylindrical barrel and concave end-domes, well within the allowable +/- 3.0 K isothermal boundary envelope [6, 7]."
    ),
    (
        "Gaseous nitrogen (GN2) PID trim-heater loop response during transition from cold-soak (-65 deg C) to hot-balance (+85 deg C).",
        "The GN2 closed-loop proportional-integral-derivative controller delivers a steady ramp rate of 1.15 K/min without exceeding the 2.0 K flight hardware thermal overshoot margin at the setpoint transition [8, 9]."
    ),
    (
        "Multi-Layer Insulation (MLI) blanket seam radiative heat leak coefficients under collimated solar simulator flux.",
        "Experimental heat flux sensor data shows the effective blanket emittance (e-star) rises from 0.024 to 0.041 at sewn seams and titanium grounding button penetrations under 1.2 solar constant flux [10, 11]."
    ),
    (
        "High-vacuum cryopump regeneration cycle scheduling and turbomolecular roughing cross-over pressure at 1e-2 Torr.",
        "To prevent hydrocarbon backstreaming from the dry mechanical backing train, the high-vacuum cryopump cross-over valve is scheduled to trigger at 8.2e-3 Torr following roughing line pump-down [12, 13]."
    ),
    (
        "Shroud high-emissivity black copper paint (Aeroglaze Z306) degradation and solar absorptance (alpha/epsilon) shift under prolonged vacuum UV exposure.",
        "Optical coupon measurements show the thermal emissivity remains stable at epsilon = 0.915, while solar absorptance exhibits an alpha delta of +0.028 after 250 equivalent sun hours of vacuum UV irradiation [14, 15]."
    ),
    (
        "Heat pipe evaporator-to-condenser thermal conductance delta under 0-g test orientation in TVAC chamber cradle.",
        "Axial-groove aluminum-ammonia heat pipes demonstrate steady thermal conductance of 36.5 W/K, maintaining an evaporator-to-condenser delta-T below 1.4 K across the adiabatic transport section [16, 17]."
    ),
    (
        "Cryogenic shroud LN2 subcooler boil-off phase-separator pressure oscillations at 2.2 bar(g).",
        "Modulating the phase-separator proportional relief bypass valve eliminates acoustic thermo-acoustic oscillations, maintaining steady single-phase subcooled liquid feed to the shroud panels [18, 19]."
    ),
    (
        "Solar simulator xenon-arc collimation beam non-uniformity mapping across payload 3-meter aperture.",
        "A 49-point radiometric radiometer survey confirms solar simulator beam irradiance uniformity within +/- 3.2% across the full 3.0 m diameter payload test circle [20, 21]."
    ),
    (
        "Type T (copper-constantan) thermocouple vacuum feedthrough thermal EMF drift during 72-hour thermal equilibrium plateau.",
        "Thermal feedthrough isothermal reference block telemetry confirms junction drift remains under 0.12 K across the 72-hour dwell, within the calibrated measurement uncertainty budget [22, 23]."
    ),
    (
        "Thermal vacuum chamber cold-wall pumping speed for water vapor desorbing from composite payload panels.",
        "At 80 K shroud surface temperature, the effective condensation pumping speed for water vapor desorbed from carbon-fiber cyanate-ester composite panels reaches approximately 125,000 L/s [24, 25]."
    ),
    (
        "Payload thermal balance test steady-state criteria (temperature rate-of-change dT/dt < 0.5 K/hour over 4 consecutive hours).",
        "Telemetry across all 16 designated thermal balance reference points demonstrates an average drift rate of dT/dt = 0.22 K/hr across a 5-hour window, successfully achieving test plateau criteria [26, 27]."
    ),
    (
        "Shroud zone GN2 heater duct flow distribution manifolds to eliminate dead zones during thermal cycling.",
        "Adjustable differential orifice plates in the GN2 supply headers equalize gas mass distribution, limiting manifold transit temperature variance to < 1.8 K between inner and outer loops [28, 29]."
    ),
    (
        "Passive cold plate thermal strap flexible copper-foil joint contact resistance in high vacuum.",
        "High-purity annealed copper foil thermal straps clamped with indium interface shims under 1.2 Nm torque achieve contact thermal resistance of 0.075 K/W per bolted interface in hard vacuum [30, 31]."
    ),
    (
        "Residual gas analyzer (RGA) mass spectrum monitoring for hydrocarbon contamination (AMU 43, 57) before solar simulator lamp ignition.",
        "RGA quadrupole mass scans show hydrocarbon baseline partial pressures for AMU 43 and 57 remain below 4.5e-11 Torr, verifying that the optical chamber is free from condensable organic contamination [32, 33]."
    ),
    (
        "Battery pack thermal runaway containment during vacuum charging/discharging qualification cycles.",
        "Integrated phase-change material heat sink plates and aerogel inter-cell barrier sheets constrain neighboring lithium-ion cell casing temperature rise to < 16 K during simulated electrical overcharge [34, 35]."
    ),
    (
        "Chamber repressurization protocol using ultra-pure dry gaseous nitrogen (GN2) to prevent moisture condensation on optical mirrors.",
        "Controlled dry GN2 repressurization at a gas temperature of +30 deg C with moisture content < 1 ppmv ensures mirror optical surface temperatures stay at least 15 K above the nitrogen gas dew point [36, 37]."
    ),
    (
        "Optical solar reflector (OSR) silvered quartz radiator tile thermal stress under rapid cryogenic shroud quenching.",
        "Thermo-elastic finite element analysis confirms that peak peel and lap-shear stresses across silicone adhesive joints remain at 38% of allowable yield under maximum cryogenic quench rates [38, 39]."
    ),
    (
        "Cryo-shroud vacuum jacket thermal barrier vacuum loss and cryopump thermal load escalation.",
        "Vacuum jacket annular pressure remains stable at 1.8e-5 Torr, confirming integrity of the guard vacuum with zero thermal load transfer to secondary stage Gifford-McMahon cryo-coolers [40, 41]."
    ),
    (
        "Satellite deployed solar array sun-tracking drive mechanism cold-start torque testing at -110 deg C.",
        "Actuator telemetry indicates cold-breakaway torque of 4.8 Nm at -110 deg C with perfluoropolyether grease lubrication, providing a 3.5x safety margin over stepper motor holding torque [42, 43]."
    ),
    (
        "Shroud dual-phase LN2/GN2 mixer valve cavitation and piping vibration acoustic spikes at 180 Hz.",
        "Installing multi-stage perforated disc pressure letdown trims in the mixer injection manifold attenuates acoustic vibration peaks by 18 dB, resolving piping acoustic resonance [44, 45]."
    ),
    (
        "Radiative heat transfer view factors between satellite antenna boom and corner corner-cube shroud panels.",
        "Monte Carlo ray-tracing simulations confirm a radiative view factor F = 0.942 between the deployed graphite-epoxy antenna boom and the active cold shroud absorption array [46, 47]."
    ),
    (
        "Thermally conductive RTV silicone filler outgassing and CVCM compliance with ECSS-Q-ST-70-02C.",
        "Post-bakeout micro-gravimetric testing confirms collected volatile condensable material (CVCM) of 0.018% and total mass loss (TML) of 0.45%, fully satisfying space qualification standards [48, 49]."
    ),
    (
        "Transient thermal response during eclipse simulation (abrupt solar simulator shutter closure for 45 minutes).",
        "During simulated orbital eclipse, spacecraft payload electronics deck temperature decays from +28.5 deg C to +19.8 deg C over 45 minutes, correlating with SINDA thermal models within 0.7 K [50, 51]."
    ),
    (
        "Cryogenic valve seat leakage rate into high-vacuum test chamber measured by helium leak detector.",
        "Mass spectrometer helium leak checks across all cryogenic valve stems and shutoff seats confirm leak rates below 8.0e-10 mbar*L/s under 6 bar proof pressure [52, 53]."
    ),
    (
        "Payload multi-node thermal nodal network (SINDA/FLUINT) correlation with TVAC thermocouple channel telemetry.",
        "The correlated mathematical model achieves a standard error of estimate of 1.28 K across 180 physical thermocouple locations, satisfying flight acceptance model validation requirements [54, 55]."
    ),
    (
        "Shroud pressure relief safety burst disk burst pressure verification at 16 bar during rapid emergency warm-up.",
        "Dual reverse-buckling burst disk assemblies were hydrostatically qualified at 16.0 +/- 0.4 bar(g), ensuring passive overpressure relief during catastrophic cryogen boil-off scenarios [56, 57]."
    ),
    (
        "Star tracker baffle thermal guard ring heater power margins during extreme cold soak.",
        "Guard ring heater power consumption measures 7.2 W at 50% pulse-width duty cycle during -75 deg C soak, providing an operational control power margin of 50% [58, 59]."
    ),
    (
        "Thermal stabilization plateau criteria across 128 telemetry thermocouple channels before initiating radiometric calibrations.",
        "All 128 flight thermocouple channels meet the strict radiometric stability criterion (dT/dt < 0.05 K/hr over 6 consecutive hours), clearing the optical payload for mission calibration [60, 61]."
    ),
    (
        "Summary telemetry evaluation across all 6 thermal-vacuum cycle phases (hot soak, cold soak, transitions, and vacuum bakeout).",
        "Multi-phase telemetry synthesis across 480 cumulative TVAC chamber test hours validates spacecraft thermal control subsystem compliance, verifying flight acceptance margins under extreme orbit conditions [62, 63]."
    ),
]

for q, a in topics_c13:
    c13_msgs.append({"role": "user", "content": q})
    c13_msgs.append({"role": "assistant", "content": a})

c13_msgs.append({
    "role": "user",
    "content": "Please search external thermal-vacuum test repositories for multi-mission satellite qualification TVAC chamber test logs, cryogenic shroud cooldown profiles, and thermal stabilization datasets."
})

cases.append({
    "name": "case_13_researcher",
    "dataset": DATASET,
    "description": "Evaluation case 13: Conducting an extensive multi-turn engineering consultation on orbital satellite thermal-vacuum (TVAC) chamber cryogenic shroud control and thermal stabilization (32 turns context)",
    "catalog": CATALOG,
    "system_prompt": SYSTEM_PROMPT,
    "messages": c13_msgs,
    "target": """A valid A2UI payload rendering a SourceImportCard component alongside a comprehensive domain research synthesis:
1. **SourceImportCard Structure**: The UI must render a SourceImportCard component with a descriptive summary of high-vacuum orbital satellite environmental test chamber (TVAC) cryogenic shroud control and thermal stabilization containing 5 relevant source items covering flight qualification TVAC chamber logs, liquid nitrogen shroud cooldown profiles, thermal balance equilibrium criteria, and vacuum outgassing telemetry.
2. **Source Item Metadata**: Each source item in the card must include a clear, descriptive title, a valid URL string, and appropriate source metadata (such as sourceType, sourceName, or summary).
3. **Domain Synthesis Quality**: The accompanying assistant response must synthesize key spacecraft thermal engineering findings addressing cryogenic shroud temperature control, vacuum thermal stabilization criteria, and multi-mission qualification test datasets, supported by numbered citations ([1], [2], etc.).""",
})


# ==============================================================================
# Case 14: Global commercial apparel supply chain sustainability risk matrix
# (3 dimensions: labor standards, raw material traceability, microplastics;
# 7 slots in SourceImportCard; 1 message / 1 turn context)
# ==============================================================================
cases.append({
    "name": "case_14_researcher",
    "dataset": DATASET,
    "description": "Evaluation case 14: Sourcing external enterprise risk management data across a 3-dimension apparel supply chain sustainability risk matrix (1 turns context)",
    "catalog": CATALOG,
    "system_prompt": SYSTEM_PROMPT,
    "messages": [
        {
            "role": "user",
            "content": """Act as a senior global apparel supply chain and corporate sustainability consultant. Please conduct a comprehensive risk screening for global commercial apparel manufacturing networks across three analytical risk dimensions:

1. Labor Standards & Ethical Workplace Practices (ILO core conventions compliance, living wage benchmark disparities, forced labor audit verifications, and Tier-1 factory versus Tier-3 subcontracting transparency).
2. Raw Material Traceability & Sustainable Sourcing (certified organic cotton chain of custody, viscose deforestation-risk screening, recycled polyester GRS feedstock verification, and stable isotope provenance testing).
3. Synthetic Microplastics & Wastewater Effluents (synthetic microfiber shedding rates during industrial wet processing, ZDHC wastewater guidelines, hazardous chemical discharge, and microplastic effluent filtration mandates).

Please synthesize the technical and industry literature and generate an A2UI SourceImportCard indexing 7 authoritative sustainability standards, regulatory compliance frameworks, and textile supply chain research sources.""",
        },
    ],
    "target": """A valid A2UI payload rendering a SourceImportCard component alongside a comprehensive domain research synthesis:
1. **SourceImportCard Structure**: The UI must render a SourceImportCard component with a descriptive summary of global commercial apparel supply chain sustainability risk containing 7 relevant source items covering ILO labor standards, raw material traceability protocols, textile microplastic shedding research, and ZDHC wastewater compliance.
2. **Source Item Metadata**: Each source item in the card must include a clear, descriptive title, a valid URL string, and appropriate source metadata (such as sourceType, sourceName, or summary).
3. **Domain Synthesis Quality**: The accompanying assistant response must deliver a structured sustainability risk matrix addressing the 3 dimensions (Labor Standards, Raw Material Traceability, Synthetic Microplastics & Wastewater Effluents), incorporating empirical risk benchmarks and supported by numbered citations ([1], [2], etc.).""",
})


# ==============================================================================
# Case 15: Municipal public library board of trustees & regional arts council
# executive director appointments (official gazette verification;
# 3 slots in SourceImportCard; 1 message / 1 turn context)
# ==============================================================================
cases.append({
    "name": "case_15_researcher",
    "dataset": DATASET,
    "description": "Evaluation case 15: Sourcing updated administrative leadership appointments for municipal library trustees and regional arts council executives (1 turns context)",
    "catalog": CATALOG,
    "system_prompt": SYSTEM_PROMPT,
    "messages": [
        {
            "role": "user",
            "content": "Can you check who currently holds executive leadership appointments on the Municipal Public Library Board of Trustees and the Regional Arts Council? Please verify the newly appointed Board President and Executive Director successors against official municipal gazette filings, library board trustee resolution logs, and statutory council appointment registers.",
        },
    ],
    "target": """A valid A2UI payload rendering a SourceImportCard component alongside a comprehensive domain research synthesis:
1. **SourceImportCard Structure**: The UI must render a SourceImportCard component with a descriptive summary of municipal public library and regional arts council executive leadership appointments containing 3 relevant source items covering official municipal gazettes, library board of trustees resolution filings, and regional arts council appointment registers.
2. **Source Item Metadata**: Each source item in the card must include a clear, descriptive title, a valid URL string, and appropriate source metadata (such as sourceType, sourceName, or summary).
3. **Domain Synthesis Quality**: The accompanying assistant response must deliver verified leadership rosters, statutory board responsibilities, and official municipal gazette appointment dates, supported by numbered citations ([1], [2], etc.).""",
})


# Validate against dataset schema
schema = json.load(open("eval/datasets/dataset_schema.json"))
jsonschema.validate(instance=cases, schema=schema)
print("Schema validation successful!")

# Output to temp_docs/batch_3.yaml
# We use custom yaml dumper to format multiline strings nicely
class CleanDumper(yaml.SafeDumper):
    pass

def str_presenter(dumper, data):
    if "\n" in data:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

CleanDumper.add_representer(str, str_presenter)

with open("temp_docs/batch_3.yaml", "w") as f:
    yaml.dump(cases, f, Dumper=CleanDumper, sort_keys=False, width=1000, allow_unicode=True)

print(f"Successfully wrote {len(cases)} cases to temp_docs/batch_3.yaml")
