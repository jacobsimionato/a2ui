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

import sys
sys.path.insert(0, 'eval/scripts')
from cases_part1 import SYSTEM_PROMPT, CATALOG, DATASET

cases = []

# Case 11
cases.append({
    "name": "case_11_researcher",
    "dataset": DATASET,
    "description": "Evaluation case 11: Gathering public financial and contractual compensation metrics across municipal seawater reverse osmosis desalination EPC concessions (2 turns context)",
    "catalog": CATALOG,
    "system_prompt": SYSTEM_PROMPT,
    "messages": [
        {
            "role": "user",
            "content": "What are the contracted capital expenditure figures and tariff indexation formulas for the Carlsbad Seawater Desalination Project 30-year Water Purchase Agreement?",
        },
        {
            "role": "assistant",
            "content": """Based on municipal bond disclosure filings and public utility commission records, the Carlsbad Seawater Desalination Project operates under a 30-year Water Purchase Agreement (WPA) structured around two primary payment components [1-3]:

* **Fixed Capital & Base Operation Charge**: Approximately $2,100 to $2,300 per acre-foot (indexed annually to CPI-U and debt service amortization on $922M in private activity revenue bonds) [1].
* **Variable Operating & Energy Component**: Pass-through electricity consumption indexed to San Diego Gas & Electric industrial tariffs, tied to an energy consumption benchmark of approximately 3.4 to 3.6 kWh per cubic meter [2].
* **Take-or-Pay Minimum Quantity Guarantee**: A committed minimum volume of 48,000 acre-feet (~59 million cubic meters) per year [3].

Would you like to explore comparable public EPC contract metrics for other large-scale reverse osmosis facilities, such as the Sorek B plant or Taweelah desalination complex?""",
        },
        {
            "role": "user",
            "content": "Yes, please retrieve authoritative contractual metrics, energy recovery device efficiencies, and water tariff formulas across major global municipal SWRO concession contracts.",
        },
    ],
    "target": """A valid A2UI payload rendering a SourceImportCard component alongside a comprehensive domain research synthesis:
1. **SourceImportCard Structure**: The UI must render a SourceImportCard component with a descriptive summary of municipal seawater reverse osmosis (SWRO) desalination EPC contracts containing 4 relevant source items covering capital expenditure benchmarks, water purchase agreement tariff formulas, energy recovery guarantees, and municipal bond disclosures.
2. **Source Item Metadata**: Each source item in the card must include a clear, descriptive title, a valid URL string, and appropriate source metadata (such as sourceType, sourceName, or summary).
3. **Domain Synthesis Quality**: The accompanying assistant response must synthesize key infrastructure finance and engineering findings comparing fixed vs variable concession charges and energy consumption benchmarks, supported by numbered citations ([1], [2], etc.).""",
})

# Case 12
cases.append({
    "name": "case_12_researcher",
    "dataset": DATASET,
    "description": "Evaluation case 12: Performing multi-angle legal intelligence analysis of an international maritime salvage arbitration and vessel collision apportionment dispute (3 turns context)",
    "catalog": CATALOG,
    "system_prompt": SYSTEM_PROMPT,
    "messages": [
        {
            "role": "user",
            "content": "Please provide a structured procedural analysis of the admiralty collision and salvage dispute between the container vessel MV Pacific Horizon and the chemical tanker MT Nordic Stream under the 1910 Collision Convention and Lloyd's Open Form (LOF 2020).",
        },
        {
            "role": "assistant",
            "content": """Here is a structured procedural analysis of the maritime casualty dispute [1-4]:

1. **Jurisdictional Forum & Arbitration Clauses**: The LOF 2020 contract executed at sea mandates Lloyd's Salvage Arbitration in London governed by English maritime law, whereas tortious collision cross-claims remain subject to Singapore High Court admiralty jurisdiction [1].
2. **Liability Apportionment under 1910 Collision Convention**: Preliminary nautical assessor testimony indicates mutual COLREGS violations (Rule 15 crossing situation and Rule 19 restricted visibility radar plotting failures), establishing an initial 60/40 comparative fault allocation [2].
3. **SCOPIC Clause Invocation & Special Compensation**: The salvors invoked the SCOPIC clause within 24 hours of attendance, guaranteeing operational tariff remuneration plus a 25% uplift in the event that salvage property value proves insufficient to cover pollution prevention expenses [3].
4. **General Average Declaration**: Cargo interests have been called upon to post General Average bonds under the York-Antwerp Rules 2016 for port of refuge towage expenses [4].""",
        },
        {
            "role": "user",
            "content": "What are the key defenses available to cargo underwriters regarding whether vessel unseaworthiness at the commencement of the voyage bars the shipowner from claiming General Average contribution?",
        },
        {
            "role": "assistant",
            "content": """Under Rule D of the York-Antwerp Rules read alongside Article III Rule 1 of the Hague-Visby Rules, cargo underwriters can defeat General Average contributions by establishing actionable fault [1, 2]:

* **Burden of Proof**: Once cargo demonstrates that unseaworthiness caused the casualty, the burden shifts to the carrier to prove due diligence was exercised [1].
* **Judicial Precedent (The CMA CGM Libra [2021] UKSC 51)**: A defective passage plan prepared prior to departure constitutes initial unseaworthiness, depriving the carrier of crew navigation fault exemptions [2].

The current workspace documents do not contain the recent regional appellate rulings or the London arbitration award excerpts for this specific casualty. Would you like me to search external legal databases?""",
        },
        {
            "role": "user",
            "content": "Yes, please search external legal databases for regional appellate admiralty court rulings and arbitration awards interpreting SCOPIC environmental defense remuneration.",
        },
    ],
    "target": """A valid A2UI payload rendering a SourceImportCard component alongside a comprehensive domain research synthesis:
1. **SourceImportCard Structure**: The UI must render a SourceImportCard component with a descriptive summary of international maritime salvage arbitration and collision liability containing 4 relevant source items covering Lloyd's Open Form jurisprudence, SCOPIC clauses, York-Antwerp Rules, and judicial admiralty precedents.
2. **Source Item Metadata**: Each source item in the card must include a clear, descriptive title, a valid URL string, and appropriate source metadata (such as sourceType, sourceName, or summary).
3. **Domain Synthesis Quality**: The accompanying assistant response must synthesize key legal findings addressing salvage remuneration, due diligence unseaworthiness defenses under Hague-Visby Rule D, and SCOPIC tariff structures, supported by numbered citations ([1], [2], etc.).""",
})

# Case 13 (63 messages: 31 back-and-forth turns + 1 final user prompt)
c13_msgs = []
topics_c13 = [
    ("Inducer inlet pressure oscillations at 85% rated power", "Analysis indicates tip leakage vortex cavitation producing sub-synchronous rotating cavitation at 0.72x shaft speed [1]."),
    ("Blade back-sweep angle trade-off (78 deg vs 84 deg)", "Increasing back-sweep to 84 deg reduces blade incidence angle and extends cavitation margins by 14% at partial flow [2]."),
    ("Thermodynamic suppression effect in liquid methane vs LOX", "Liquid methane exhibits significant evaporative cooling suppression in cavitation bubbles, lowering B-factor by ~2.1 [3]."),
    ("Casing acoustic emission transducer readings at 12 kHz", "Acoustic emission spectral power indicates stable sheet cavitation without severe bubble collapse micro-pitting [4]."),
    ("Suction specific speed (Nss) threshold limits for stable operation", "Recommended Nss operating envelope is bounded between 22,000 and 26,500 (gpm units) to avoid surging [5]."),
    ("Hub boundary layer bleed recirculation slots", "Circumferential casing treatment grooves delay rotating stall onset and suppress backflow cavitation vortices [6]."),
    ("Inducer leading edge wedge angle profile sharpening", "A modified circular leading edge profile with 4-degree wedge angle reduces stagnation pressure shock loss [7]."),
    ("Axial thrust balancing cavity pressure oscillations", "Balancing piston orifice leakage responds dynamically to cavitation-induced discharge pressure swings [8]."),
    ("Rotordynamic cross-coupled stiffness coefficients", "Cavitation alters shroud fluid annulus forces, introducing negative direct stiffness and destabilizing swirl [9]."),
    ("High-frequency unsteady wall pressure transducer spectra", "High-speed sensors reveal discrete blade-passing frequency harmonics alongside broad-band cavitation noise [10]."),
    ("Propellant inlet subcooling margin at main tank interface", "Subcooling margin must remain above 3.5 K to prevent vapor locking during throttled engine restart [11]."),
    ("Bearing coolant flow bypass starvation during cavitation breakdown", "Hydrostatic bearing film thickness contracts by 18% during 3% head drop cavitation breakdown [12]."),
    ("Inducer blade surface micro-texture anti-erosion coatings", "Titanium aluminum nitride (TiAlN) PVD coating demonstrates 4x cavitation erosion lifetime compared to bare Inconel 718 [13]."),
    ("Transient chill-down flow boiling in pump volute", "Two-phase chill-down models demonstrate stable film boiling transition to nucleate boiling within 12 seconds [14]."),
    ("Blade structural high-cycle fatigue (HCF) stress resonance", "Campbell diagram analysis identifies 3rd engine order intersection with first torsional blade mode at 28,500 RPM [15]."),
    ("Vane-island diffuser throat blockage effects", "Cavitation clouds shedding from inducer blades cause periodic aerodynamic blockage at downstream diffuser vanes [16]."),
    ("Shaft seal secondary purge gas leakage interaction", "Helium purge gas entrainment into inducer inlet stream increases effective fluid compressibility [17]."),
    ("Dynamic response to rapid throttle ramp from 60% to 100%", "Transient cavitation pocket growth lags commanded acceleration by approximately 45 ms [18]."),
    ("Cavitation compliance and mass flow gain factors for POGO stability", "Experimentally derived cavitation compliance C_c = -0.045 cm^3/Pa provides key inputs for vehicle POGO filters [19]."),
    ("Cryogenic fluid property variations near critical point", "Proximity to thermodynamic critical point enhances vapor density and dampens pressure pulsation amplitudes [20]."),
    ("Two-phase CFD multiphase Schnerr-Sauer cavitation models", "CFD grid refinement at inducer leading edge confirms accurate prediction of sheet cavitation length within 6% of strobe imagery [21]."),
    ("Stator vane clocking orientation relative to volute tongue", "Clocking optimization reduces pressure pulse reflection back into the inducer exit plane by 22% [22]."),
    ("Inducer shroud abradable seal material compatibility with cryogenic LOX", "Nickel-graphite abradable seals show zero particulate ignition hazard in pressurized LOX flammability testing [23]."),
    (" cavitation erosion pit morphology on suction surfaces", "SEM micrographs demonstrate ductile micro-void coalescence from high-velocity liquid micro-jet impacts [24]."),
    ("Inducer blade thickness taper distribution from hub to tip", "Cubic polynomial thickness taper provides optimal balance between structural rigidity and blade passage area [25]."),
    ("Inlet guide vane swirl pre-rotation impact on incidence angle", "Positive pre-swirl vanes reduce relative inlet flow velocity and lower blade leading edge cavitation inception number [26]."),
    ("Secondary flow leakage through inducer tip clearance gap (0.25 mm vs 0.40 mm)", "Tightening tip clearance to 0.25 mm reduces tip leakage vortex cavitation volume by 35% [27]."),
    ("Vortex shedding frequency locking with discharge line acoustics", "Helmholtz acoustic resonance in the discharge duct locks with inducer blade shedding frequency at 420 Hz [28]."),
    ("Multi-variable throttled hot-fire test run vibration signatures", "Accelerometer telemetry indicates triaxial vibration remains below 15 g RMS throughout steady-state burns [29]."),
    ("Turbine exhaust gas bypass mixer cavitation impact", "Hot gas injection for tank pressurization maintains thermal boundary layer without destabilizing inducer inlet [30]."),
    ("Telemetry summary across all 30 test stand hot-fire cycles", "Full parameter synthesis confirms structural health of inducer blades across 4,200 cumulative seconds of run time [31]."),
]

for q, a in topics_c13:
    c13_msgs.append({"role": "user", "content": q})
    c13_msgs.append({"role": "assistant", "content": a})

c13_msgs.append({
    "role": "user",
    "content": "Please search external telemetry repositories for the multi-year flight certification turbopump test runs and hot-fire vibration data."
})

cases.append({
    "name": "case_13_researcher",
    "dataset": DATASET,
    "description": "Evaluation case 13: Conducting an extensive multi-turn system parameters consultation on cryogenic rocket turbopump inducer cavitation dynamics (32 turns context)",
    "catalog": CATALOG,
    "system_prompt": SYSTEM_PROMPT,
    "messages": c13_msgs,
    "target": """A valid A2UI payload rendering a SourceImportCard component alongside a comprehensive domain research synthesis:
1. **SourceImportCard Structure**: The UI must render a SourceImportCard component with a descriptive summary of cryogenic turbopump inducer cavitation dynamics containing 5 relevant source items covering flight certification hot-fire test datasets, tip leakage vortex suppressions, suction specific speed benchmarks, and POGO cavitation compliance models.
2. **Source Item Metadata**: Each source item in the card must include a clear, descriptive title, a valid URL string, and appropriate source metadata (such as sourceType, sourceName, or summary).
3. **Domain Synthesis Quality**: The accompanying assistant response must synthesize key fluid dynamics findings addressing turbopump cavitation margins, vibration frequency spectra, and test run datasets, supported by numbered citations ([1], [2], etc.).""",
})

# Case 14
cases.append({
    "name": "case_14_researcher",
    "dataset": DATASET,
    "description": "Evaluation case 14: Sourcing external enterprise risk management data across a 3-category geomechanical carbon capture and storage (CCS) reservoir integrity matrix (1 turns context)",
    "catalog": CATALOG,
    "system_prompt": SYSTEM_PROMPT,
    "messages": [
        {
            "role": "user",
            "content": """Act as a senior subsurface geomechanics and geological carbon storage consultant. Please conduct a comprehensive risk screening for long-term supercritical CO2 sequestration in deep saline aquifers.
Organize your evaluation across a 3-category analytical risk matrix:
1. Geomechanical Integrity (caprock hydraulic fracture pressure, effective stress changes, and fault slip reactivation).
2. Geochemical Reactivity (supercritical CO2-brine-rock dissolution kinetics, mineral trapping, and cement sheath degradation).
3. Hydrogeological Containment (overpressure plume migration, legacy wellbore leakage pathways, and freshwater aquifer monitoring).
Synthesize the technical literature and generate an A2UI SourceImportCard indexing authoritative peer-reviewed geomechanics and carbon storage research sources.""",
        },
    ],
    "target": """A valid A2UI payload rendering a SourceImportCard component alongside a comprehensive domain research synthesis:
1. **SourceImportCard Structure**: The UI must render a SourceImportCard component with a descriptive summary of geomechanical carbon capture and storage (CCS) reservoir integrity containing 7 relevant source items covering caprock integrity, fault reactivation risk, supercritical CO2 mineralization, and legacy wellbore leakage monitoring.
2. **Source Item Metadata**: Each source item in the card must include a clear, descriptive title, a valid URL string, and appropriate source metadata (such as sourceType, sourceName, or summary).
3. **Domain Synthesis Quality**: The accompanying assistant response must synthesize key geomechanical findings structured around the 3-category analytical matrix (Geomechanical Integrity, Geochemical Reactivity, Hydrogeological Containment), incorporating quantitative pore-pressure criteria and supported by numbered citations ([1], [2], etc.).""",
})

# Case 15
cases.append({
    "name": "case_15_researcher",
    "dataset": DATASET,
    "description": "Evaluation case 15: Sourcing updated administrative leadership appointments for marine protected area (MPA) management authorities and benthic recovery councils (1 turns context)",
    "catalog": CATALOG,
    "system_prompt": SYSTEM_PROMPT,
    "messages": [
        {
            "role": "user",
            "content": "Can you check who currently holds executive leadership appointments on the National Marine Protected Area (MPA) Authority and Regional Benthic Habitat Recovery Advisory Council? Please search official gazette filings and government environmental publications to verify active directors and statutory committee chairs.",
        },
    ],
    "target": """A valid A2UI payload rendering a SourceImportCard component alongside a comprehensive domain research synthesis:
1. **SourceImportCard Structure**: The UI must render a SourceImportCard component with a descriptive summary of marine protected area leadership appointments containing 3 relevant source items covering official government gazettes, statutory marine conservation authority boards, and scientific benthic council rosters.
2. **Source Item Metadata**: Each source item in the card must include a clear, descriptive title, a valid URL string, and appropriate source metadata (such as sourceType, sourceName, or summary).
3. **Domain Synthesis Quality**: The accompanying assistant response must deliver verified leadership rosters, statutory board responsibilities, and official gazette appointment dates, supported by numbered citations ([1], [2], etc.).""",
})

# Case 16
cases.append({
    "name": "case_16_researcher",
    "dataset": DATASET,
    "description": "Evaluation case 16: Auditing, verifying, and reconciling missing or mismatched academic citations in archaeological paleobotany radiocarbon calibration datasets (1 turns context)",
    "catalog": CATALOG,
    "system_prompt": SYSTEM_PROMPT,
    "messages": [
        {
            "role": "user",
            "content": """I am finalizing the scholarly apparatus for my academic monograph on Holocene vegetation transitions and agricultural dispersal in the Eastern Mediterranean.
Several in-text radiocarbon age determinations and pollen zone biozone correlations contain missing or mismatched bibliographic citations:
1. Van Zeist and Bottema (1991) Lake Zeribar pollen diagram biozones.
2. Reimer et al. (2020) IntCal20 northern hemisphere calibration curve discrepancies for 8.2 ka event tree rings.
3. Roberts et al. (2001) Lake Van stable isotope varve chronologies.
4. Bottema and Sarpaki (1994) Santorini volcanic ash layer archaeobotanical macrofossils.
Please audit these references, reconcile missing bibliographic data, verify calibrated radiocarbon ranges (cal BP), and emit an A2UI SourceImportCard indexing verified scholarly citations.""",
        },
    ],
    "target": """A valid A2UI payload rendering a SourceImportCard component alongside a comprehensive domain research synthesis:
1. **SourceImportCard Structure**: The UI must render a SourceImportCard component with a descriptive summary of Holocene paleobotany and radiocarbon calibration datasets containing 6 relevant source items covering IntCal20 calibration datasets, Lake Zeribar and Lake Van pollen biozone chronologies, and archaeobotanical macrofossil studies.
2. **Source Item Metadata**: Each source item in the card must include a clear, descriptive title, a valid URL string, and appropriate source metadata (such as sourceType, sourceName, or summary).
3. **Domain Synthesis Quality**: The accompanying assistant response must deliver a structured bibliographic audit reconciling in-text citations, providing calibrated radiocarbon dates (cal BP), and detailing paleoenvironmental biozone chronologies, supported by numbered citations ([1], [2], etc.).""",
})

# Case 17
cases.append({
    "name": "case_17_researcher_headless_create_artifact",
    "dataset": DATASET,
    "description": "Evaluation case 17: Comprehensive pedagogical curriculum design and statutory procedural analysis for hospital antimicrobial stewardship and disinfection compliance (5 turns context)",
    "catalog": CATALOG,
    "system_prompt": SYSTEM_PROMPT,
    "messages": [
        {
            "role": "user",
            "content": "I need a polished presentation slide deck on hospital environmental infection control, UV-C terminal disinfection validation, and EPA List K disinfectant efficacy standards for multi-drug resistant organisms.",
        },
        {
            "role": "assistant",
            "content": """Here is an outline for the **Hospital Infection Control & UV-C Disinfection** presentation slide deck [1-3]:

* **Slide 1: Epidemiology of Healthcare-Associated Infections (HAIs)**: Multi-drug resistant organism (MDRO) surface survival times (C. auris, MRSA, C. difficile) [1].
* **Slide 2: Chemical Disinfection & EPA List Protocols**: Contact time requirements, quaternary ammonium vs sporicidal peracetic acid / hydrogen peroxide formulations [2].
* **Slide 3: Automated UV-C Terminal Disinfection Physics**: 254 nm germicidal irradiation vs 222 nm Far-UVC, inverse-square law shadow zones, and radiometer dosing validation [3].
* **Slide 4: Standard Operating Procedures (SOPs)**: Terminal cleaning checklists, ATP bioluminescence swab auditing, and CDC environmental cleaning guidelines.""",
        },
        {
            "role": "user",
            "content": "Slide 3 needs a deeper comparative analysis between pulsed-xenon UV (PX-UV) systems and continuous low-pressure mercury vapor systems regarding cycle time and shadowing mitigation.",
        },
        {
            "role": "assistant",
            "content": """Integrating a comparative technology matrix on Slide 3 provides critical technical rigor [1, 2]:

* **Continuous Low-Pressure Mercury Vapor (254 nm)**: Emits a continuous monochromatic peak; requires 20-45 minute runtimes for 4-log reduction of spores; highly dependent on robotic placement to prevent room shadowing [1].
* **Pulsed-Xenon UV (PX-UV)**: Generates broad-spectrum germicidal pulses (200-320 nm) at high energy density; achieves bactericidal reduction in 5-10 minute cycles; shorter cycle times facilitate multi-position room repositioning [2].""",
        },
        {
            "role": "user",
            "content": "We also need to incorporate regulatory compliance mandates from the Joint Commission Infection Prevention Standards (IC.02.02.01) and OSHA hazardous drug surface decontamination. Are those in our workspace?",
        },
        {
            "role": "assistant",
            "content": """Our current workspace documents focus on general clinical disinfection guidelines but lack specific statutory text for Joint Commission standard IC.02.02.01 and OSHA USP <800> hazardous drug surface deactivation mandates [1].

I can conduct an external search for Joint Commission accreditation audit criteria and clinical trials evaluating pulsed-xenon disinfection efficacy against C. auris outbreaks. Would you like me to proceed?""",
        },
        {
            "role": "user",
            "content": "Please generate a presentation slide deck on acoustic impact modeling and marine mammal mitigation protocols in offshore wind construction.",
        },
    ],
    "target": """A valid A2UI payload rendering a SourceImportCard component alongside a comprehensive domain research synthesis:
1. **SourceImportCard Structure**: The UI must render a SourceImportCard component with a descriptive summary of hospital infection control and environmental disinfection compliance containing 6 relevant source items covering CDC environmental cleaning guidelines, UV-C dosimetric validation, EPA List K sporicidal efficacy, and Joint Commission standards.
2. **Source Item Metadata**: Each source item in the card must include a clear, descriptive title, a valid URL string, and appropriate source metadata (such as sourceType, sourceName, or summary).
3. **Domain Synthesis Quality**: The accompanying assistant response must synthesize key hospital infection control protocols, presentation slide layouts, and statutory compliance standards, supported by numbered citations ([1], [2], etc.).""",
})

# Case 18
cases.append({
    "name": "case_18_researcher",
    "dataset": DATASET,
    "description": "Evaluation case 18: Sourcing competitive performance meta-strategy data, evaluating autonomous electric racing vehicle battery thermal management and downforce drag trade-offs (1 turns context)",
    "catalog": CATALOG,
    "system_prompt": SYSTEM_PROMPT,
    "messages": [
        {
            "role": "user",
            "content": "What are the top contender vehicle control strategies and latest aerodynamic/battery thermal management meta for the upcoming 100 km Autonomous Super Formula e-Prix at Suzuka? Please analyze the trade-offs between aggressive regenerative braking energy recovery (front/rear motor split), pouch cell thermal de-rating above 55 deg C, and active DRS aerodynamic flap deployment.",
        },
    ],
    "target": """A valid A2UI payload rendering a SourceImportCard component alongside a comprehensive domain research synthesis:
1. **SourceImportCard Structure**: The UI must render a SourceImportCard component with a descriptive summary of autonomous electric racing meta-strategy and powertrain thermal management containing 3 relevant source items covering battery thermal de-rating curves, torque-vectoring regenerative split algorithms, and active aerodynamic downforce control.
2. **Source Item Metadata**: Each source item in the card must include a clear, descriptive title, a valid URL string, and appropriate source metadata (such as sourceType, sourceName, or summary).
3. **Domain Synthesis Quality**: The accompanying assistant response must deliver a structured competitive performance analysis evaluating battery thermal limits, regenerative braking balance, and aerodynamic DRS flap deployment tiers, supported by numbered citations ([1], [2], etc.).""",
})

# Case 19 (25 messages: 12 back-and-forth turns + 1 final prompt)
c19_msgs = []
topics_c19 = [
    ("Please verify the immediate memory items for dual-engine flameout at FL350 from our Boeing 777 Flight Crew Operations Manual (FCOM).", "Immediate memory items: (1) Pitch down to maintain 270 knots minimum airspeed for windmill start envelope; (2) Thrust levers idle; (3) Engine Start Selectors to FLT; (4) APU Start switch to START [1]."),
    ("What are the altitude boundaries between windmill relight and starter-assisted relight?", "The windmill relight envelope requires minimum 250-270 KIAS below FL300. Above FL300 or below 250 KIAS, APU bleed air or starter assistance is mandatory to achieve minimum 15% N2 core speed [2]."),
    ("How does APU autostart sequencing function when electrical buses are shed to the emergency battery tie?", "The APU fuel valve opens automatically via the hot battery bus, and dedicated battery-powered APU electric starter cranks up to 55% N1 before transferring AC power to essential AC bus 1 [3]."),
    ("What is the optimal glide speed profile (L/D max) for maximum range versus maximum endurance?", "Maximum glide range speed is approximately 230 KIAS at clean configuration (~2.5 nautical miles per 1,000 feet loss); maximum endurance (holding) speed is ~205 KIAS [4]."),
    ("Review the Ram Air Turbine (RAT) deployment conditions and hydraulic pressure supply.", "The RAT deploys automatically upon dual AC transfer bus de-energization, supplying 3,000 psi hydraulic pressure exclusively to the flight control center hydraulic system and primary flight controls [5]."),
    ("Check the electrical load management during standby power operation.", "On standby power, captain's flight instruments, standby compass, VHF radio 1, and left engine crossfeed valves remain powered; all non-essential galley and utility buses are shed [6]."),
    ("What is the ditching preparation sequence if relight is unachievable below 10,000 feet?", "Ditching sequence: transmit MAYDAY on 121.5 MHz; set transponder 7700; unlatch flight deck door; select DITCHING pb ON to close outflow valves below waterline; land parallel to swell crests [7]."),
    ("Detail the landing configuration with zero thrust and RAT hydraulic power.", "Approach configuration: Flaps 20 maximum; gear down via alternate gravity extension at 1,500 ft AGL; Vref + 20 knots approach speed; ground spoilers manual deployment upon touchdown [8]."),
    ("What are the fuel crossfeed balancing instructions in the event of asymmetric fuel supply?", "Ensure fuel crossfeed switches are open only when balancing wings; if fuel leak is suspected, isolate the leaking wing tank immediately and do not crossfeed [9]."),
    ("How does flight control law degradation manifest during dual engine failure?", "Flight controls transition from Normal Law to Secondary Mode: envelope protections (stall, overspeed, bank angle) are lost; yaw damper remains active via RAT hydraulic pressure [10]."),
    ("Summarize the procedural steps for windshield anti-ice and pitot probe heat on battery backup.", "Left pitot and captain angle-of-attack probes remain heated by the standby inverter; windshield anti-ice heating is load-shed [11]."),
    ("Review communication protocol with Air Traffic Control and cabin crew preparation.", "Execute emergency descent callout; alert cabin crew with 'CABIN CREW, ADVISORY 5 MINUTES'; ensure passenger emergency oxygen masks are NOT deployed if cabin altitude remains below 14,000 ft [12]."),
]

for q, a in topics_c19:
    c19_msgs.append({"role": "user", "content": q})
    c19_msgs.append({"role": "assistant", "content": a})

c19_msgs.append({
    "role": "user",
    "content": "Generate an interactive Quick Reference Handbook (QRH) emergency checklist card summarizing all 12 operational procedures with source references."
})

cases.append({
    "name": "case_19_create_artifact_researcher_headless",
    "dataset": DATASET,
    "description": "Evaluation case 19: Extracting dual-engine flameout and emergency airspeed recovery procedures from commercial aviation flight operations manuals into quick-reference handbooks (13 turns context)",
    "catalog": CATALOG,
    "system_prompt": SYSTEM_PROMPT,
    "messages": c19_msgs,
    "target": """A valid A2UI payload rendering a SourceImportCard component alongside a comprehensive domain research synthesis:
1. **SourceImportCard Structure**: The UI must render a SourceImportCard component with a descriptive summary of commercial aviation emergency procedures and dual-engine flameout recovery containing 2 relevant source items covering flight crew operations manuals (FCOM) and quick reference handbook (QRH) checklists.
2. **Source Item Metadata**: Each source item in the card must include a clear, descriptive title, a valid URL string, and appropriate source metadata (such as sourceType, sourceName, or summary).
3. **Domain Synthesis Quality**: The accompanying assistant response must synthesize procedural emergency actions, detailing memory items, relight envelope airspeeds, and electrical/hydraulic backup configurations, supported by numbered citations ([1], [2], etc.).""",
})

# Case 20
cases.append({
    "name": "case_20_researcher",
    "dataset": DATASET,
    "description": "Evaluation case 20: Initiating an open-ended exploratory research inquiry into subglacial Antarctic lake astrobiology and chemolithoautotrophic metabolic pathways (3 turns context)",
    "catalog": CATALOG,
    "system_prompt": SYSTEM_PROMPT,
    "messages": [
        {
            "role": "user",
            "content": "I want to start a new exploratory scientific research project in this empty workspace.",
        },
        {
            "role": "assistant",
            "content": """Welcome! I can assist you in scoping, structuring, and researching your new project from the ground up.

To help establish the appropriate workspace foundations, could you clarify:
1. **Target Scientific Domain**: What specific field (e.g., planetary astrobiology, deep-subsurface extremophile genomics, cryogenic oceanography) will we focus on?
2. **Core Research Objectives**: Are you preparing a grant proposal, literature review, or computational modeling framework?
3. **Primary Methodological Scope**: Will you be analyzing genomic metagenomic data, geochemical mass-spectrometry surveys, or planetary analog field studies?""",
        },
        {
            "role": "user",
            "content": "Let's focus on subglacial Antarctic lakes (such as Lake Vostok and Mercer Subglacial Lake) as terrestrial analogs for the icy moons Europa and Enceladus. Specifically, how do chemolithoautotrophic microbial ecosystems survive beneath 4,000 meters of ice without solar photons?",
        },
        {
            "role": "assistant",
            "content": """Subglacial Antarctic lakes represent extraordinary analogs for astrobiological exploration of Europa and Enceladus.

Key metabolic and geochemical research avenues include:
* **Chemolithoautotrophic Energy Coupling**: Microbial oxidation of reduced iron (Fe2+) and sulfur (S0, H2S) coupled to sulfate reduction and methanogenesis driven by subglacial bedrock comminution and radiolysis.
* **Geothermal Heat Flux & Ice Sheet Basal Melting**: Subglacial geothermal gradients driving convective circulation within deep brine water columns.
* **Extreme Dissolved Oxygen Supersaturation**: High-pressure gas hydrate clathrate melting injecting hyper-oxygenated fluids into deep benthic zones.

Would you like me to conduct a multi-disciplinary literature survey across astrobiology, glaciology, and metagenomics repositories to establish our research foundation?""",
        },
        {
            "role": "user",
            "content": "Yes, please conduct a comprehensive multi-disciplinary search covering all areas: chemolithoautotrophic pathways, radiolysis, iron-sulfur cycling, and planetary analog comparisons for Europa and Enceladus.",
        },
    ],
    "target": """A valid A2UI payload rendering a SourceImportCard component alongside a comprehensive domain research synthesis:
1. **SourceImportCard Structure**: The UI must render a SourceImportCard component with a descriptive summary of subglacial Antarctic lake astrobiology and extremophile metabolic pathways containing 9 relevant source items (1 text report slot plus 8 web sources) covering chemolithoautotrophy, sulfur-iron biogeochemistry, subglacial hydrology, and icy moon planetary analog models.
2. **Source Item Metadata**: Each source item in the card must include a clear, descriptive title, a valid URL string, and appropriate source metadata (such as sourceType, sourceName, or summary).
3. **Domain Synthesis Quality**: The accompanying assistant response must synthesize key astrobiological findings across all requested domains (chemoautotrophy, radiolysis, iron-sulfur cycling, planetary analogs), structured with clear scientific headings and supported by numbered citations ([1], [2], etc.).""",
})

import pprint
with open('eval/scripts/cases_part2.py', 'w') as f:
    f.write(f'''# Copyright 2024 Google LLC
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

"""Synthetic evaluation cases 11 to 20."""

from cases_part1 import SYSTEM_PROMPT, CATALOG, DATASET

CASES_PART_2 = {repr(cases)}
''')

print(f"Successfully generated cases_part2.py with {len(cases)} cases")
