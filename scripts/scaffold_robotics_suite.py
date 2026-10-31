"""Scaffold the 39-pair robotics/industrial skill suite (builder + checklist reviewer).

Each pair becomes axiom-<base> (builder) and axiom-<base>-review (reviewer)
under skills/, plus catalog.yaml / registry.yaml entries. Deterministic and
rerunnable: generated skill files are always rewritten from SPEC; catalog and
registry entries are appended only when the id is absent.

All prose is original AxiomEmbedded content. Standards are referenced by
number/title/edition/clause only; no normative text is reproduced. Skills
whose basis is a de-facto middleware spec (ROS 2, Nav2, behavior trees, URDF,
TF) declare standards: [] and name the de-facto reference in the body.

Usage: python scripts/scaffold_robotics_suite.py [--check]
--check verifies every expected file/entry exists without writing.
"""
from __future__ import annotations
import pathlib
import sys
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]

# standard -> (edition, clauses considered)
STD_INFO = {
    "ANSI/RIA R15.06-2012": ("2012", "robot and robot-system requirements"),
    "ISO 10218-1:2011": ("2011", "5 (robot design, stop functions)"),
    "ISO 10218-2:2011": ("2011", "4 (integration, safeguarding)"),
    "ISO 12100:2010": ("2010", "5 (risk assessment, risk reduction)"),
    "ISO 13849-1:2023": ("2023", "6 (PLr determination, categories)"),
    "ISO/TS 15066:2016": ("2016", "5 (collaborative modes, contact events)"),
    "ISO 13849-2:2012": ("2012", "validation of safety functions"),
    "ISO 13850:2015": ("2015", "4 (emergency stop)"),
    "ISO 14118:2017": ("2017", "4 (restart, isolation, LOTO context)"),
    "ISO 11161:2007": ("2007", "5 (integrated manufacturing systems layout)"),
    "ISO 3691-4:2023": ("2023", "4-6 (driverless-truck safety, detection)"),
    "ISO 9283:1998": ("1998", "test poses, path metrics"),
    "IEC 62061:2021": ("2021", "6, 7 (SIL determination, SRS)"),
    "IEC 61508:2010": ("2010", "7 (background capability)"),
    "IEC 62443-2-1:2010": ("2010", "security program elements"),
    "IEC 62443-3-2:2020": ("2020", "zones/conduits, risk assessment"),
    "IEC 62443-3-3:2013": ("2013", "system security requirements"),
    "IEC 62657:2017": ("2017", "wireless coexistence method"),
    "ANSI Z244.1-2016": ("2016", "hazardous-energy control steps"),
    "EU 2023/1230": ("2023", "machinery safety requirements"),
    "ISO/IEC 23894:2023": ("2023", "AI risk-management guidance"),
    "ISO/IEC 23053:2022": ("2022", "AI decision-making framework"),
}

LIFECYCLE = ["requirements", "architecture", "design", "implementation",
             "integration", "verification", "validation", "release"]

# base, title, domain, subdomain, category, desc, platforms, standards,
# artifacts, risk, inputs, outputs, project-use note, assurance link or ""
SPEC: list[dict] = [
    {"base": "ansi-r1506-compliance-matrix", "title": "ANSI/RIA R15.06 Compliance Matrix",
     "domain": "industrial", "subdomain": "compliance", "category": "compliance",
     "desc": "Builds a clause-by-claim compliance matrix for ANSI/RIA R15.06 robot-system safety, aligned to ISO 10218, with an evidence pointer per claim.",
     "platforms": ["mcu", "mpu"], "standards": ["ANSI/RIA R15.06-2012", "ISO 10218-1:2011", "ISO 10218-2:2011"],
     "artifacts": ["compliance matrix", "evidence index"], "risk": "high",
     "inputs": ["requirement list", "design evidence", "prior audit findings"],
     "outputs": ["compliance matrix", "open-claim list"],
     "use": "US robot-system compliance evidence", "assurance": ""},
    {"base": "behavior-tree-spec", "title": "Behavior-Tree Specification",
     "domain": "robotics", "subdomain": "middleware", "category": "design",
     "desc": "Specifies behavior-tree structure for a robot task controller: node types, blackboard keys, tick semantics, and failure-handling contracts.",
     "platforms": ["mpu", "soc"], "standards": [],
     "artifacts": ["behavior-tree spec", "node contract table"], "risk": "medium",
     "inputs": ["task description", "existing tree or pseudocode", "interface list"],
     "outputs": ["behavior-tree spec", "node contract table"],
     "use": "Deterministic task-control design (de-facto: BehaviorTree.CPP / py_trees conventions)", "assurance": ""},
    {"base": "cobot-hand-guiding", "title": "Cobot Hand-Guiding Design",
     "domain": "robotics", "subdomain": "robot-safety", "category": "design",
     "desc": "Designs hand-guiding collaborative operation: enabling-device logic, reduced-speed limits, mode transitions, and stop behavior.",
     "platforms": ["mpu", "soc"], "standards": ["ISO/TS 15066:2016", "ISO 10218-1:2011"],
     "artifacts": ["hand-guiding design", "speed-limit table"], "risk": "safety-critical",
     "inputs": ["cobot model", "task list", "risk assessment"],
     "outputs": ["hand-guiding design", "speed-limit table"],
     "use": "Collaborative hand-guiding mode design", "assurance": ""},
    {"base": "dataset-documentation", "title": "Dataset Documentation",
     "domain": "robotics", "subdomain": "ai-data", "category": "documentation",
     "desc": "Documents robotics datasets: provenance, licensing, splits, labeling protocol, sensor calibration notes, and known biases.",
     "platforms": ["mpu", "soc"], "standards": ["ISO/IEC 23894:2023", "ISO/IEC 23053:2022"],
     "artifacts": ["dataset card", "labeling protocol"], "risk": "medium",
     "inputs": ["dataset location", "collection notes", "license terms"],
     "outputs": ["dataset card", "labeling protocol"],
     "use": "AI data governance for perception datasets", "assurance": ""},
    {"base": "declaration-of-conformity", "title": "Declaration of Conformity Pack",
     "domain": "industrial", "subdomain": "compliance", "category": "compliance",
     "desc": "Assembles the declaration-of-conformity evidence pack: applicable legislation, standards applied, responsible person, and artifact pointers.",
     "platforms": ["mcu", "mpu"], "standards": ["EU 2023/1230", "ISO 12100:2010"],
     "artifacts": ["conformity pack", "standards-applied list"], "risk": "high",
     "inputs": ["machine scope", "risk assessment", "test evidence"],
     "outputs": ["conformity pack", "standards-applied list"],
     "use": "Market-placement conformity evidence", "assurance": ""},
    {"base": "eoat-spec", "title": "End-of-Arm Tooling Specification",
     "domain": "robotics", "subdomain": "cell-integration", "category": "design",
     "desc": "Specifies end-of-arm tooling: gripper forces, tool-change interface, vacuum/magnetic retention, and retained-risk assumptions.",
     "platforms": ["mpu", "soc"], "standards": ["ISO 10218-1:2011", "ISO 10218-2:2011"],
     "artifacts": ["EOAT spec", "gripper force budget"], "risk": "high",
     "inputs": ["workpiece data", "cycle-time target", "robot payload"],
     "outputs": ["EOAT spec", "gripper force budget"],
     "use": "Gripper and tooling integration design", "assurance": ""},
    {"base": "fleet-manager-architecture", "title": "Fleet-Manager Architecture",
     "domain": "robotics", "subdomain": "motion-navigation", "category": "design",
     "desc": "Architects fleet-manager task assignment, traffic rules, map/zone interfaces, and deadlock handling for multi-AMR operation.",
     "platforms": ["mpu", "soc"], "standards": ["ISO 3691-4:2023"],
     "artifacts": ["fleet architecture", "traffic-rule set"], "risk": "high",
     "inputs": ["fleet size", "site map", "mission list"],
     "outputs": ["fleet architecture", "traffic-rule set"],
     "use": "Multi-AMR fleet coordination design", "assurance": ""},
    {"base": "iec62061-sil", "title": "IEC 62061 SIL Determination",
     "domain": "industrial", "subdomain": "compliance", "category": "assessment",
     "desc": "Determines SIL targets per safety function and writes software/system safety requirements with verification criteria.",
     "platforms": ["mcu", "mpu"], "standards": ["IEC 62061:2021", "IEC 61508:2010"],
     "artifacts": ["SIL determination", "safety requirements specification"], "risk": "safety-critical",
     "inputs": ["hazard list", "severity/exposure data", "architecture sketch"],
     "outputs": ["SIL determination", "safety requirements specification"],
     "use": "SIL targets and safety requirements", "assurance": ""},
    {"base": "iec62443-risk-assessment", "title": "IEC 62443 Risk Assessment",
     "domain": "industrial", "subdomain": "ot-security", "category": "assessment",
     "desc": "Runs an OT cyber-risk assessment: consequence analysis, threat scenarios, SL-target proposal, and mitigation mapping.",
     "platforms": ["mcu", "mpu"], "standards": ["IEC 62443-3-2:2020", "IEC 62443-3-3:2013"],
     "artifacts": ["OT risk assessment", "SL-target proposal"], "risk": "high",
     "inputs": ["zone sketch", "asset inventory", "threat model"],
     "outputs": ["OT risk assessment", "SL-target proposal"],
     "use": "OT security risk and SL targeting", "assurance": "axiom-threat-model"},
    {"base": "interlock-estop-architecture", "title": "Interlock and E-Stop Architecture",
     "domain": "robotics", "subdomain": "robot-safety", "category": "design",
     "desc": "Architects the interlock chain and e-stop topology: channels, stop categories, restart behavior, and defeat monitoring.",
     "platforms": ["mpu", "soc"], "standards": ["ISO 14118:2017", "ISO 13850:2015", "ISO 13849-1:2023"],
     "artifacts": ["interlock architecture", "e-stop topology"], "risk": "safety-critical",
     "inputs": ["cell layout", "safety-function list", "risk assessment"],
     "outputs": ["interlock architecture", "e-stop topology"],
     "use": "Guarding and stop-system design", "assurance": ""},
    {"base": "iso10218-compliance-matrix", "title": "ISO 10218 Compliance Matrix",
     "domain": "robotics", "subdomain": "compliance", "category": "compliance",
     "desc": "Builds a clause-by-claim compliance matrix for ISO 10218-1 and ISO 10218-2 with an evidence pointer per claim.",
     "platforms": ["mpu", "soc"], "standards": ["ISO 10218-1:2011", "ISO 10218-2:2011"],
     "artifacts": ["compliance matrix", "evidence index"], "risk": "high",
     "inputs": ["requirement list", "design evidence", "risk assessment"],
     "outputs": ["compliance matrix", "open-claim list"],
     "use": "Robot/cell compliance evidence", "assurance": ""},
    {"base": "iso12100-risk-assessment", "title": "ISO 12100 Risk Assessment",
     "domain": "industrial", "subdomain": "compliance", "category": "assessment",
     "desc": "Runs hazard identification, risk estimation, and risk-reduction recording for machinery per ISO 12100, with residual-risk statements.",
     "platforms": ["mcu", "mpu"], "standards": ["ISO 12100:2010"],
     "artifacts": ["risk assessment", "residual-risk register"], "risk": "high",
     "inputs": ["machine limits", "task list", "incident history"],
     "outputs": ["risk assessment", "residual-risk register"],
     "use": "Machinery risk assessment record", "assurance": "axiom-hazard-risk"},
    {"base": "iso13849-plr", "title": "ISO 13849 PLr Determination",
     "domain": "robotics", "subdomain": "robot-safety", "category": "design",
     "desc": "Determines the required Performance Level (PLr) per safety function and allocates subsystem targets for later verification.",
     "platforms": ["mpu", "soc"], "standards": ["ISO 13849-1:2023"],
     "artifacts": ["PLr determination", "safety-function list"], "risk": "safety-critical",
     "inputs": ["hazard list", "severity/frequency data", "architecture sketch"],
     "outputs": ["PLr determination", "safety-function list"],
     "use": "PLr targets for safety functions", "assurance": "axiom-safety-requirements"},
    {"base": "iso15066-biomechanical-limits", "title": "ISO/TS 15066 Biomechanical Limits",
     "domain": "robotics", "subdomain": "robot-safety", "category": "assessment",
     "desc": "Records applicable body-region force/pressure limits and transfers them into PFL thresholds and measurement points.",
     "platforms": ["mpu", "soc"], "standards": ["ISO/TS 15066:2016"],
     "artifacts": ["biomechanical limit set", "threshold transfer table"], "risk": "high",
     "inputs": ["contact scenarios", "body regions exposed", "payload data"],
     "outputs": ["biomechanical limit set", "threshold transfer table"],
     "use": "Contact-limit evidence for PFL", "assurance": ""},
    {"base": "iso3691-4-risk-assessment", "title": "ISO 3691-4 Risk Assessment",
     "domain": "industrial", "subdomain": "compliance", "category": "assessment",
     "desc": "Runs risk assessment for driverless-truck deployment: operating zones, detection performance, braking, and traffic interaction.",
     "platforms": ["mcu", "mpu"], "standards": ["ISO 3691-4:2023", "ISO 12100:2010"],
     "artifacts": ["AMR risk assessment", "detection-requirement set"], "risk": "high",
     "inputs": ["site layout", "truck specification", "traffic plan"],
     "outputs": ["AMR risk assessment", "detection-requirement set"],
     "use": "Driverless-truck deployment safety case", "assurance": ""},
    {"base": "iso9283-performance-test", "title": "ISO 9283 Performance Test",
     "domain": "robotics", "subdomain": "cell-integration", "category": "verification",
     "desc": "Specifies pose-accuracy and path-repeatability tests: test poses, loads, speeds, measurement method, and acceptance thresholds.",
     "platforms": ["mpu", "soc"], "standards": ["ISO 9283:1998"],
     "artifacts": ["performance test spec", "threshold table"], "risk": "medium",
     "inputs": ["robot model", "accuracy requirements", "measurement equipment"],
     "outputs": ["performance test spec", "threshold table"],
     "use": "Manipulator performance verification", "assurance": ""},
    {"base": "loto-procedure", "title": "Lockout/Tagout Procedure",
     "domain": "industrial", "subdomain": "cell-integration", "category": "procedure",
     "desc": "Writes lockout/tagout procedures: energy sources, isolation points, lock application order, and zero-energy verification steps.",
     "platforms": ["mcu", "mpu"], "standards": ["ISO 14118:2017", "ANSI Z244.1-2016"],
     "artifacts": ["LOTO procedure", "isolation-point map"], "risk": "high",
     "inputs": ["energy-source survey", "cell layout", "maintenance tasks"],
     "outputs": ["LOTO procedure", "isolation-point map"],
     "use": "Hazardous-energy control during maintenance", "assurance": ""},
    {"base": "machinery-safety-lifecycle-plan", "title": "Machinery Safety Lifecycle Plan",
     "domain": "industrial", "subdomain": "compliance", "category": "compliance",
     "desc": "Plans the machinery safety lifecycle: milestones, review gates, and evidence deliverables from concept through decommissioning.",
     "platforms": ["mcu", "mpu"], "standards": ["ISO 12100:2010", "EU 2023/1230"],
     "artifacts": ["lifecycle plan", "evidence-gate list"], "risk": "high",
     "inputs": ["project phases", "machine scope", "regulatory path"],
     "outputs": ["lifecycle plan", "evidence-gate list"],
     "use": "End-to-end safety-activity planning", "assurance": ""},
    {"base": "model-card", "title": "Model Card",
     "domain": "robotics", "subdomain": "ai-data", "category": "documentation",
     "desc": "Authors model cards for robotics ML models: intended use, metrics, limits, failure modes, and deployment caveats.",
     "platforms": ["mpu", "soc"], "standards": ["ISO/IEC 23894:2023"],
     "artifacts": ["model card"], "risk": "medium",
     "inputs": ["model identifier", "eval results", "deployment context"],
     "outputs": ["model card"],
     "use": "ML model transparency record", "assurance": ""},
    {"base": "nav2-config", "title": "Nav2 Configuration",
     "domain": "robotics", "subdomain": "motion-navigation", "category": "design",
     "desc": "Designs Nav2 planner/controller/costmap configuration with deterministic parameter records and behavior-tree plugin selection.",
     "platforms": ["mpu", "soc"], "standards": [],
     "artifacts": ["Nav2 parameter set", "costmap review"], "risk": "medium",
     "inputs": ["robot footprint", "map data", "behavior requirements"],
     "outputs": ["Nav2 parameter set", "costmap review"],
     "use": "Mobile-base navigation tuning (de-facto: Nav2 parameter and plugin conventions)", "assurance": ""},
    {"base": "operating-envelope", "title": "Operating Envelope Definition",
     "domain": "robotics", "subdomain": "cell-integration", "category": "design",
     "desc": "Defines the operating envelope: spaces, modes, speed/force boundaries, and permitted transitions between collaborative and automatic operation.",
     "platforms": ["mpu", "soc"], "standards": ["ISO 10218-2:2011", "ISO/TS 15066:2016"],
     "artifacts": ["operating envelope", "mode-transition table"], "risk": "high",
     "inputs": ["cell layout", "task list", "risk assessment"],
     "outputs": ["operating envelope", "mode-transition table"],
     "use": "Boundary definition for mixed-mode operation", "assurance": ""},
    {"base": "operator-training-matrix", "title": "Operator Training Matrix",
     "domain": "industrial", "subdomain": "cell-integration", "category": "procedure",
     "desc": "Matrices roles to required training modules, refresh intervals, and competence evidence for robot-cell personnel.",
     "platforms": ["mcu", "mpu"], "standards": ["ISO 10218-2:2011", "ISO 12100:2010"],
     "artifacts": ["training matrix", "competence record template"], "risk": "medium",
     "inputs": ["role list", "task risk levels", "regulatory duties"],
     "outputs": ["training matrix", "competence record template"],
     "use": "Personnel competence evidence", "assurance": ""},
    {"base": "ot-asset-inventory", "title": "OT Asset Inventory",
     "domain": "industrial", "subdomain": "ot-security", "category": "assessment",
     "desc": "Inventories OT assets: devices, firmware versions, protocols, network attachment, and ownership for security management.",
     "platforms": ["mcu", "mpu"], "standards": ["IEC 62443-2-1:2010", "IEC 62443-3-2:2020"],
     "artifacts": ["OT asset inventory", "ownership register"], "risk": "medium",
     "inputs": ["network diagrams", "device lists", "scan results"],
     "outputs": ["OT asset inventory", "ownership register"],
     "use": "Security-managed asset baseline", "assurance": ""},
    {"base": "perception-test-catalog", "title": "Perception Test Catalog",
     "domain": "robotics", "subdomain": "ai-data", "category": "assessment",
     "desc": "Catalogs perception tests: scenarios, ground-truth method, metrics, pass thresholds, and dataset traceability.",
     "platforms": ["mpu", "soc"], "standards": ["ISO/IEC 23894:2023"],
     "artifacts": ["perception test catalog", "metric-threshold table"], "risk": "high",
     "inputs": ["perception requirements", "datasets", "sensor spec"],
     "outputs": ["perception test catalog", "metric-threshold table"],
     "use": "Perception validation planning", "assurance": ""},
    {"base": "pfl-plan", "title": "Power-and-Force-Limiting Plan",
     "domain": "robotics", "subdomain": "robot-safety", "category": "design",
     "desc": "Designs the power-and-force-limiting regime: contact scenarios, force/pressure thresholds, and measurement verification points.",
     "platforms": ["mpu", "soc"], "standards": ["ISO/TS 15066:2016"],
     "artifacts": ["PFL plan", "contact-scenario table"], "risk": "safety-critical",
     "inputs": ["collaborative tasks", "biomechanical limits", "payload data"],
     "outputs": ["PFL plan", "contact-scenario table"],
     "use": "Contact-safety design for cobots", "assurance": ""},
    {"base": "robot-acceptance-protocol", "title": "Robot Acceptance Protocol",
     "domain": "robotics", "subdomain": "cell-integration", "category": "verification",
     "desc": "Defines the acceptance protocol: FAT/SAT stages, test criteria, performance sampling, and sign-off evidence.",
     "platforms": ["mpu", "soc"], "standards": ["ISO 10218-2:2011", "ISO 9283:1998"],
     "artifacts": ["acceptance protocol", "sign-off record"], "risk": "high",
     "inputs": ["contract requirements", "cell design", "safety functions"],
     "outputs": ["acceptance protocol", "sign-off record"],
     "use": "Factory and site acceptance evidence", "assurance": ""},
    {"base": "robot-cell-layout", "title": "Robot Cell Layout",
     "domain": "robotics", "subdomain": "cell-integration", "category": "design",
     "desc": "Lays out the robot cell: fences, gates, light curtains, operator stations, material flow, and maintenance access.",
     "platforms": ["mpu", "soc"], "standards": ["ISO 10218-2:2011", "ISO 11161:2007"],
     "artifacts": ["cell layout", "safeguarding schedule"], "risk": "high",
     "inputs": ["equipment list", "floor plan", "task sequence"],
     "outputs": ["cell layout", "safeguarding schedule"],
     "use": "Cell geometry and safeguarding placement", "assurance": ""},
    {"base": "robot-cell-scope", "title": "Robot Cell Scope Definition",
     "domain": "robotics", "subdomain": "cell-integration", "category": "design",
     "desc": "Defines robot-cell scope: equipment list, boundaries, external interfaces, and integrator versus user responsibilities.",
     "platforms": ["mpu", "soc"], "standards": ["ISO 10218-2:2011", "ISO 11161:2007"],
     "artifacts": ["cell scope", "responsibility matrix"], "risk": "high",
     "inputs": ["stakeholder notes", "site survey", "equipment list"],
     "outputs": ["cell scope", "responsibility matrix"],
     "use": "Cell boundary and responsibility framing", "assurance": "axiom-scope-context"},
    {"base": "robot-field-acceptance", "title": "Robot Field Acceptance",
     "domain": "robotics", "subdomain": "cell-integration", "category": "verification",
     "desc": "Plans on-site acceptance: installation checks, safeguarding verification, production-trial criteria, and punch-list management.",
     "platforms": ["mpu", "soc"], "standards": ["ISO 10218-2:2011"],
     "artifacts": ["field-acceptance plan", "punch list"], "risk": "high",
     "inputs": ["acceptance protocol", "installation record", "site constraints"],
     "outputs": ["field-acceptance plan", "punch list"],
     "use": "Site acceptance execution record", "assurance": ""},
    {"base": "robot-hil-test-catalog", "title": "Robot HIL Test Catalog",
     "domain": "robotics", "subdomain": "cell-integration", "category": "assessment",
     "desc": "Catalogs hardware-in-the-loop tests for robot safety functions: fault injection, timing measurement, and coverage mapping.",
     "platforms": ["mpu", "soc"], "standards": ["ISO 13849-2:2012", "ISO 10218-2:2011"],
     "artifacts": ["HIL test catalog", "coverage map"], "risk": "high",
     "inputs": ["safety-function list", "HIL rig capability", "V&V plan"],
     "outputs": ["HIL test catalog", "coverage map"],
     "use": "Safety-function test coverage evidence", "assurance": "axiom-vnv-plan"},
    {"base": "robot-sop", "title": "Robot Standard Operating Procedure",
     "domain": "industrial", "subdomain": "cell-integration", "category": "procedure",
     "desc": "Writes standard operating procedures: startup, mode changes, fault recovery, and shutdown for robot-cell operators.",
     "platforms": ["mcu", "mpu"], "standards": ["ISO 10218-2:2011", "ISO 12100:2010"],
     "artifacts": ["SOP set", "fault-recovery cards"], "risk": "medium",
     "inputs": ["operating envelope", "control design", "incident history"],
     "outputs": ["SOP set", "fault-recovery cards"],
     "use": "Repeatable safe operation", "assurance": ""},
    {"base": "ros2-system-architecture", "title": "ROS 2 System Architecture",
     "domain": "robotics", "subdomain": "middleware", "category": "design",
     "desc": "Architects the ROS 2 system: node graph, topics/services/actions, QoS choices, executors, and lifecycle management.",
     "platforms": ["mpu", "soc"], "standards": [],
     "artifacts": ["node-graph architecture", "interface contract"], "risk": "medium",
     "inputs": ["functional requirements", "sensor/actuator list", "compute budget"],
     "outputs": ["node-graph architecture", "interface contract"],
     "use": "Middleware structure design (de-facto: ROS 2 design conventions)", "assurance": ""},
    {"base": "safety-io-matrix", "title": "Safety I/O Matrix",
     "domain": "robotics", "subdomain": "robot-safety", "category": "design",
     "desc": "Maps safety inputs and outputs to controllers: test pulses, discrepancy monitoring, and proof-test intervals.",
     "platforms": ["mpu", "soc"], "standards": ["ISO 13849-1:2023", "IEC 62061:2021"],
     "artifacts": ["safety I/O matrix", "proof-test schedule"], "risk": "safety-critical",
     "inputs": ["safety-function list", "controller spec", "wiring design"],
     "outputs": ["safety I/O matrix", "proof-test schedule"],
     "use": "Safety wiring and diagnostics design", "assurance": ""},
    {"base": "ssm-plan", "title": "Speed-and-Separation-Monitoring Plan",
     "domain": "robotics", "subdomain": "robot-safety", "category": "design",
     "desc": "Designs speed-and-separation monitoring: protective zones, speed mapping, sensor coverage claims, and stop-performance budgets.",
     "platforms": ["mpu", "soc"], "standards": ["ISO/TS 15066:2016", "ISO 10218-2:2011"],
     "artifacts": ["SSM plan", "zone map"], "risk": "safety-critical",
     "inputs": ["cell layout", "operator positions", "sensor spec"],
     "outputs": ["SSM plan", "zone map"],
     "use": "Separation-based collaboration design", "assurance": ""},
    {"base": "tf-tree-spec", "title": "TF Tree Specification",
     "domain": "robotics", "subdomain": "middleware", "category": "design",
     "desc": "Specifies the TF frame tree: frame ids, parentage, update rates, static versus dynamic authority, and validation checks.",
     "platforms": ["mpu", "soc"], "standards": [],
     "artifacts": ["TF-tree spec", "frame table"], "risk": "medium",
     "inputs": ["kinematic chain", "sensor mounts", "map frame policy"],
     "outputs": ["TF-tree spec", "frame table"],
     "use": "Coordinate-frame consistency (de-facto: tf2 conventions)", "assurance": ""},
    {"base": "urdf-model-spec", "title": "URDF Model Specification",
     "domain": "robotics", "subdomain": "middleware", "category": "design",
     "desc": "Specifies the URDF model: links, joints, limits, inertial placeholders, visual/collision geometry policy, and check procedures.",
     "platforms": ["mpu", "soc"], "standards": [],
     "artifacts": ["URDF spec", "joint-limit table"], "risk": "medium",
     "inputs": ["mechanical design", "actuator limits", "sensor mounts"],
     "outputs": ["URDF spec", "joint-limit table"],
     "use": "Robot description consistency (de-facto: URDF conventions)", "assurance": ""},
    {"base": "wireless-coexistence-plan", "title": "Wireless Coexistence Plan",
     "domain": "industrial", "subdomain": "ot-security", "category": "assessment",
     "desc": "Plans wireless coexistence: spectrum survey, interference budgets, channel planning, and fallback behavior on link loss.",
     "platforms": ["mcu", "mpu"], "standards": ["IEC 62657:2017", "IEC 62443-3-3:2013"],
     "artifacts": ["coexistence plan", "channel plan"], "risk": "medium",
     "inputs": ["wireless inventory", "spectrum survey", "criticality ranking"],
     "outputs": ["coexistence plan", "channel plan"],
     "use": "Reliable industrial wireless operation", "assurance": ""},
    {"base": "zone-conduit-plan", "title": "Zone and Conduit Plan",
     "domain": "industrial", "subdomain": "ot-security", "category": "design",
     "desc": "Partitions the OT network into zones and conduits with security-level targets, conduit requirements, and firewall rules.",
     "platforms": ["mcu", "mpu"], "standards": ["IEC 62443-3-2:2020"],
     "artifacts": ["zone/conduit plan", "conduit requirement set"], "risk": "high",
     "inputs": ["network diagrams", "risk assessment", "asset inventory"],
     "outputs": ["zone/conduit plan", "conduit requirement set"],
     "use": "Segmented OT network design", "assurance": "axiom-threat-model"},
]

BUILDER_GATES = [
    ("inputs", "Inputs, scope, and prerequisites recorded"),
    ("method", "Workflow steps executed with evidence"),
    ("artifact", "Deliverable artifact complete against its template"),
    ("standards", "Applicable standard clauses addressed or explicitly deferred"),
    ("traceability", "Links to source inputs recorded"),
    ("handoff", "Open questions and reviewer handoff recorded"),
]
REVIEWER_GATES = [
    ("completeness", "Artifact present and complete against its template"),
    ("criteria", "Review criteria applied per clause or claim"),
    ("evidence", "Evidence sampled, not just asserted"),
    ("traceability", "Traceability links audited end to end"),
    ("verdict", "Verdict recorded with severity-ranked findings"),
    ("independence", "Reviewer independence recorded"),
]


def _frontmatter(sid: str, title: str, desc: str, spec: dict, related: list[str],
                 template_name: str) -> str:
    fm = {
        "name": sid, "title": title, "description": desc,
        "version": "0.1.0", "author": "PRATIK PATIL", "license": "Apache-2.0",
        "domains": [spec["domain"]], "platforms": spec["platforms"],
        "axiom": {
            "dotted_name": "axiom." + spec["domain"] + "." + spec["base"].replace("-", "."),
            "domain": spec["domain"], "subdomain": spec["subdomain"],
            "category": spec["category"], "maturity": "experimental",
            "owner": "axiom-embedded",
            "tags": [spec["subdomain"], spec["base"].split("-")[0]],
            "related_skills": related, "lifecycle": LIFECYCLE,
            "standards": spec["standards"], "artifact_types": spec["artifacts"],
            "mcp_tools": ["run_skill", "validate_skill"],
            "risk_level": spec["risk"], "review_required": True,
            "safety_critical": spec["risk"] == "safety-critical",
            "checklists": ["checklists/review.yaml"],
            "templates": ["templates/" + template_name],
            "inputs": spec["inputs"], "outputs": spec["outputs"],
            "required_tools": ["validate_skill"], "optional_tools": ["run_skill"],
        },
    }
    return "---\n" + yaml.safe_dump(fm, sort_keys=False) + "---\n"


def _map_rows(spec: dict, reviewer: bool) -> str:
    lines = ["| Standard | Edition | Clauses considered | Project use |",
             "|---|---|---|---|"]
    for std in spec["standards"]:
        edition, clauses = STD_INFO[std]
        use = ("Independent review of " + spec["artifacts"][0] + " against " + std.split(":")[0]
               if reviewer else spec["use"])
        lines.append(f"| {std.split(':')[0]} | {edition} | {clauses} | {use} |")
    if not spec["standards"]:
        lines.append("| (de-facto middleware conventions) | n/a | interface and naming rules | " +
                     ("Review consistency against project conventions" if reviewer else spec["use"]) + " |")
    return "\n".join(lines)


def _body(spec: dict, reviewer: bool, partner: str) -> str:
    role = "Independently reviews" if reviewer else "Produces"
    noun = spec["artifacts"][0]
    kind = "review" if reviewer else "build"
    lines = [
        f"# Axiom {spec['title']}" + (" Review" if reviewer else ""),
        "",
        "## Purpose",
        f"{role} the {noun} for {spec['title'].lower()} work. {spec['desc']}",
        ("This is the checklist reviewer partner of the builder skill; it never "
         "modifies the artifact, it records a verdict."
         if reviewer else
         "This is the builder skill; its output is always passed to the "
         "checklist-reviewer partner before release use."),
        "",
        "## When to Use",
        f"- The project needs the {spec['title'].lower()} {kind} workflow.",
        "- Inputs listed below are available.",
        "",
        "## When Not to Use",
        "- As a substitute for qualified safety/security certification review.",
        "- When the required inputs are absent (record the gap instead of inventing data).",
        "",
        "## Required Inputs",
    ]
    lines += [f"- {i}." for i in spec["inputs"]]
    lines += [
        "",
        "## Execution Workflow" if not reviewer else "",
        "## Review Workflow" if reviewer else "",
    ]
    if reviewer:
        lines += [
            "1. Confirm the builder artifact exists and matches its template.",
            "2. Apply each checklist gate; sample evidence, do not trust assertions.",
            "3. Audit traceability links end to end.",
            "4. Record verdict: pass, pass-with-findings, or fail, with severity-ranked findings.",
            "5. Record reviewer independence and hand back open questions.",
        ]
    else:
        lines += [
            "1. Normalize the request into objective, scope, and constraints.",
            "2. Inspect repo context and existing inputs.",
            "3. Select the skill template and fill every section.",
            "4. Validate structurally (template fields) and semantically (checklist gates).",
            "5. Record traceability to source inputs.",
            "6. Hand the artifact to the reviewer partner with open questions.",
        ]
    lines += [
        "",
        "## Standard Basis",
        _map_rows(spec, reviewer),
        "",
        "Cite number, title, edition/year, clause only. Summaries are original "
        "language; no normative text is reproduced.",
        "",
        "## Tool Invocations",
        "- `run_skill` with structured context; dry-run before writes.",
        "- `validate_skill` must pass before release use.",
        "- MCP tools: run_skill, validate_skill.",
        "",
        "## Decision Rules",
        "- Prefer explicit configuration over invented defaults; flag every assumption.",
        "- Safety/security-relevant outputs require human review (review_required: true).",
        "",
        "## Workflow",
        "Follow the workflow above; record per-step evidence in the run manifest.",
        "",
        "## Deliverables",
    ]
    lines += [f"- {o}." for o in spec["outputs"]]
    if reviewer:
        lines.append("- Review verdict with severity-ranked findings.")
    lines += [
        "",
        "## Acceptance Criteria",
        "- `validate_skill` passes; checklist gates all green; traceability complete.",
        "",
        "## Acceptance",
        "- All checklist gates pass; findings carry severity, evidence, and action.",
        "",
        f"Partner skill: {partner}.",
        "",
        "_Generated by scripts/scaffold_robotics_suite.py; all prose is original "
        "AxiomEmbedded content._",
        "",
    ]
    return "\n".join(lines)


def _catalog_entry(sid: str, title: str, desc: str, spec: dict, related: list[str]) -> dict:
    return {
        "id": sid,
        "name": "axiom." + spec["domain"] + "." + spec["base"].replace("-", "."),
        "title": title, "version": "0.1.0",
        "domain": spec["domain"], "subdomain": spec["subdomain"],
        "category": spec["category"], "maturity": "experimental",
        "owner": "axiom-embedded",
        "tags": [spec["subdomain"], spec["base"].split("-")[0]],
        "inputs": spec["inputs"], "outputs": spec["outputs"],
        "dependencies": [], "related_skills": related,
        "path": "skills/" + sid, "enabled": True,
        "standards": spec["standards"], "lifecycle": LIFECYCLE,
        "artifact_types": spec["artifacts"],
        "mcp_tools": ["run_skill", "validate_skill"],
        "risk_level": spec["risk"], "review_required": True,
    }


def build() -> dict[str, int]:
    stats = {"skills": 0, "catalog": 0, "registry": 0}
    cat_path = ROOT / "skills" / "catalog.yaml"
    reg_path = ROOT / "skills" / "registry.yaml"
    cat_ids = {e["id"] for e in yaml.safe_load(cat_path.read_text(encoding="utf-8"))["skills"]}
    reg_paths = {s["path"] for s in yaml.safe_load(reg_path.read_text(encoding="utf-8"))["skills"]}
    with cat_path.open("a", encoding="utf-8") as cat_f, \
            reg_path.open("a", encoding="utf-8") as reg_f:
        for spec in SPEC:
            builder = "axiom-" + spec["base"]
            reviewer = builder + "-review"
            for sid, is_reviewer in ((builder, False), (reviewer, True)):
                title = spec["title"] + (" Review" if is_reviewer else "")
                partner = reviewer if not is_reviewer else builder
                related = [partner] + ([spec["assurance"]] if spec["assurance"] and not is_reviewer else [])
                d = ROOT / "skills" / sid
                (d / "checklists").mkdir(parents=True, exist_ok=True)
                (d / "templates").mkdir(exist_ok=True)
                (d / "references").mkdir(exist_ok=True)
                (d / "scripts").mkdir(exist_ok=True)
                (d / "tests").mkdir(exist_ok=True)
                template_name = spec["base"] + ".template.yaml"
                (d / "SKILL.md").write_text(
                    _frontmatter(sid, title, spec["desc"], spec, related, template_name)
                    + "\n" + _body(spec, is_reviewer, partner), encoding="utf-8")
                (d / "manifest.yaml").write_text(yaml.safe_dump({
                    "id": sid, "version": "1.2.0", "contract_version": 1,
                    "type": "reusable-skill",
                    "source_of_truth": {"instructions": "SKILL.md", "contract": "manifest.yaml"},
                    "facets": {"domains": [spec["domain"]], "platforms": spec["platforms"]},
                    "standards": spec["standards"],
                    "axiom": {
                        "dotted_name": "axiom." + spec["domain"] + "." + spec["base"].replace("-", "."),
                        "maturity": "experimental", "category": spec["category"]},
                }, sort_keys=False), encoding="utf-8")
                gates = REVIEWER_GATES if is_reviewer else BUILDER_GATES
                (d / "checklists" / "review.yaml").write_text(yaml.safe_dump({
                    "gates": [{"id": gid, "text": text} for gid, text in gates],
                }, sort_keys=False), encoding="utf-8")
                (d / "references" / "standard-map.md").write_text(
                    f"# Standard map -- {sid} (original summaries, no normative text)\n\n"
                    + _map_rows(spec, is_reviewer) + "\n", encoding="utf-8")
                (d / "templates" / template_name).write_text(yaml.safe_dump({
                    "artifact": spec["artifacts"][0], "skill": sid, "version": "0.1.0",
                    "inputs_used": [], "content": {}, "open_questions": [],
                    "traceability": [], "approval_status": "pending-review",
                }, sort_keys=False), encoding="utf-8")
                stats["skills"] += 1
                if sid not in cat_ids:
                    entry = _catalog_entry(sid, title, spec["desc"], spec, related)
                    cat_f.write(yaml.safe_dump([entry], sort_keys=False))
                    cat_ids.add(sid)
                    stats["catalog"] += 1
                if f"skills/{sid}" not in reg_paths:
                    reg_f.write(yaml.safe_dump([{
                        "name": "axiom." + spec["domain"] + "." + spec["base"].replace("-", "."),
                        "path": f"skills/{sid}", "domain": spec["domain"],
                        "maturity": "experimental"}], sort_keys=False))
                    reg_paths.add(f"skills/{sid}")
                    stats["registry"] += 1
    return stats


def check() -> int:
    missing = []
    cat_ids = {e["id"] for e in yaml.safe_load(
        (ROOT / "skills" / "catalog.yaml").read_text(encoding="utf-8"))["skills"]}
    reg_paths = {s["path"] for s in yaml.safe_load(
        (ROOT / "skills" / "registry.yaml").read_text(encoding="utf-8"))["skills"]}
    for spec in SPEC:
        for sid in ("axiom-" + spec["base"], "axiom-" + spec["base"] + "-review"):
            for rel in ("SKILL.md", "manifest.yaml", "checklists/review.yaml",
                        "references/standard-map.md",
                        f"templates/{spec['base']}.template.yaml"):
                if not (ROOT / "skills" / sid / rel).exists():
                    missing.append(f"skills/{sid}/{rel}")
            if sid not in cat_ids:
                missing.append(f"catalog:{sid}")
            if f"skills/{sid}" not in reg_paths:
                missing.append(f"registry:{sid}")
    if missing:
        print("MISSING:")
        for m in missing:
            print(f"- {m}")
        return 1
    print(f"robotics suite OK: {len(SPEC)} pairs")
    return 0


if __name__ == "__main__":
    if "--check" in sys.argv:
        raise SystemExit(check())
    print(build())
