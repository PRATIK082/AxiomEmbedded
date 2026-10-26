"""Scaffold the 30 axiom-* skills + catalog.yaml + registry.yaml (deterministic, rerunnable).

Usage: python scripts/scaffold_axiom_skills.py [--check]
--check verifies every expected file exists without writing.
Original content throughout; no reference-repo text used.
"""
from __future__ import annotations
import pathlib
import sys
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]

# id, title, domain, subdomain, category, maturity, description, platforms, standards, artifacts, risk
SKILLS: list[dict] = [
 {"id": "axiom-autosar-classic-architecture", "title": "AUTOSAR Classic Architecture Review", "domain": "automotive", "subdomain": "autosar-classic", "category": "architecture", "maturity": "beta", "desc": "Reviews AUTOSAR Classic platform architecture choices, layering, and release baselines for an ECU project and produces an architecture decision record with findings.", "platforms": ["mcu", "autosar-classic"], "standards": ["AUTOSAR Classic R24-11", "ISO 26262:2018"], "artifacts": ["architecture decision record", "layering review"], "risk": "high"},
 {"id": "axiom-autosar-classic-bsw-integration", "title": "AUTOSAR Classic BSW Integration", "domain": "automotive", "subdomain": "autosar-classic", "category": "integration", "maturity": "beta", "desc": "Integrates and reviews AUTOSAR Classic BSW configuration (ARXML/BMD/RTE/OS/COM/PduR/CanIf/CanTp/Dcm/Dem/NvM/EcuM) and produces an integration report with severity-ranked findings and a validation matrix.", "platforms": ["mcu", "autosar-classic"], "standards": ["AUTOSAR Classic R24-11", "ISO 26262:2018"], "artifacts": ["integration report", "validation matrix", "configuration-change plan"], "risk": "high"},
 {"id": "axiom-autosar-rte-design", "title": "AUTOSAR RTE Design", "domain": "automotive", "subdomain": "autosar-classic", "category": "design", "maturity": "experimental", "desc": "Designs RTE ports, interfaces, runnable entities and events for Classic software components with consistency checks and traceability.", "platforms": ["mcu", "autosar-classic"], "standards": ["AUTOSAR Classic R24-11"], "artifacts": ["RTE mapping table", "interface contract"], "risk": "medium"},
 {"id": "axiom-autosar-os-config", "title": "AUTOSAR OS Configuration Review", "domain": "automotive", "subdomain": "autosar-classic", "category": "configuration", "maturity": "experimental", "desc": "Reviews AUTOSAR OS task, alarm, schedule-table and timing-protection configuration against scheduling constraints and stack assumptions.", "platforms": ["mcu", "autosar-classic"], "standards": ["AUTOSAR Classic R24-11"], "artifacts": ["OS config review", "scheduling analysis"], "risk": "high"},
 {"id": "axiom-autosar-com-stack", "title": "AUTOSAR COM Stack Review", "domain": "automotive", "subdomain": "autosar-classic", "category": "configuration", "maturity": "experimental", "desc": "Reviews COM/PduR/CanIf/CanTp signal routing, PDU mapping and gateway assumptions for Classic communication stacks.", "platforms": ["mcu", "autosar-classic"], "standards": ["AUTOSAR Classic R24-11"], "artifacts": ["COM review", "signal-routing table"], "risk": "medium"},
 {"id": "axiom-autosar-adaptive-deployment", "title": "AUTOSAR Adaptive Deployment", "domain": "automotive", "subdomain": "autosar-adaptive", "category": "deployment", "maturity": "experimental", "desc": "Designs Adaptive service deployment (ara::com manifests, execution/state management, persistency, time sync) with a deployment checklist.", "platforms": ["mpu", "autosar-adaptive"], "standards": ["AUTOSAR Adaptive R24-11"], "artifacts": ["deployment manifest review", "deployment checklist"], "risk": "high"},
 {"id": "axiom-can-network-design", "title": "CAN Network Design", "domain": "automotive", "subdomain": "networks", "category": "design", "maturity": "beta", "desc": "Designs CAN/CAN-FD network topology, identifier allocation, bus-load budgets and timing assumptions from DBC-level inputs.", "platforms": ["mcu", "autosar-classic"], "standards": ["ISO 11898"], "artifacts": ["network design", "bus-load budget"], "risk": "medium"},
 {"id": "axiom-can-stack-integration", "title": "CAN Stack Integration", "domain": "automotive", "subdomain": "networks", "category": "integration", "maturity": "experimental", "desc": "Integrates and checks CAN driver/CanIf/CanTp stacks including baud-rate, mailbox, and error-handling configuration.", "platforms": ["mcu", "autosar-classic"], "standards": ["ISO 11898"], "artifacts": ["stack integration report"], "risk": "medium"},
 {"id": "axiom-automotive-ethernet-someip", "title": "Automotive Ethernet and SOME/IP Design", "domain": "automotive", "subdomain": "networks", "category": "design", "maturity": "experimental", "desc": "Designs Ethernet topology, VLAN/TSN assumptions and SOME/IP service modeling for service-oriented ECUs.", "platforms": ["mpu", "autosar-adaptive"], "standards": ["AUTOSAR SOME/IP", "IEEE 802.1 TSN"], "artifacts": ["Ethernet design", "service model"], "risk": "medium"},
 {"id": "axiom-diagnostics-uds", "title": "UDS Diagnostics Design and Validation", "domain": "automotive", "subdomain": "diagnostics", "category": "verification", "maturity": "beta", "desc": "Designs UDS service coverage, session/security posture and negative-response matrices, and validates them with a deterministic checker script.", "platforms": ["mcu", "mpu", "autosar-classic", "autosar-adaptive"], "standards": ["ISO 14229-1", "ISO 26262:2018"], "artifacts": ["diagnostic requirements", "service matrix", "validation report"], "risk": "high"},
 {"id": "axiom-diagnostics-doip", "title": "DoIP Diagnostics Integration", "domain": "automotive", "subdomain": "diagnostics", "category": "integration", "maturity": "experimental", "desc": "Integrates DoIP discovery, routing activation and diagnostic transport for Ethernet ECUs with tester-workflow checks.", "platforms": ["mpu", "autosar-adaptive"], "standards": ["ISO 13400-2"], "artifacts": ["DoIP integration review"], "risk": "medium"},
 {"id": "axiom-vehicle-cybersecurity", "title": "Vehicle Cybersecurity Workflow", "domain": "automotive", "subdomain": "cybersecurity", "category": "security", "maturity": "experimental", "desc": "Runs a TARA-aligned cybersecurity workflow (threat model, secure boot/diag, key management, IDS/OTA concepts) producing reviewable evidence.", "platforms": ["mcu", "mpu"], "standards": ["ISO/SAE 21434"], "artifacts": ["threat model", "security review"], "risk": "safety-critical"},
 {"id": "axiom-functional-safety", "title": "Functional Safety Workflow", "domain": "automotive", "subdomain": "safety", "category": "safety", "maturity": "experimental", "desc": "Supports HARA, safety goals, FSR/TSR derivation, FMEA/FTA templates and verification-evidence structure for safety-related work.", "platforms": ["mcu", "mpu"], "standards": ["ISO 26262:2018"], "artifacts": ["safety plan", "FMEA/FTA templates", "evidence structure"], "risk": "safety-critical"},
 {"id": "axiom-adas-perception-pipeline", "title": "ADAS Perception Pipeline Design", "domain": "automotive", "subdomain": "adas", "category": "design", "maturity": "experimental", "desc": "Designs sensor-abstraction, perception interfaces and object-model contracts for ADAS pipelines.", "platforms": ["mpu", "soc"], "standards": ["ISO 26262:2018"], "artifacts": ["perception interface contract"], "risk": "high"},
 {"id": "axiom-adas-validation", "title": "ADAS Validation Planning", "domain": "automotive", "subdomain": "adas", "category": "verification", "maturity": "experimental", "desc": "Plans sensor-fusion validation, recording/replay campaigns and KPI definitions for ADAS functions.", "platforms": ["mpu", "soc"], "standards": ["ISO 26262:2018"], "artifacts": ["validation plan", "KPI set"], "risk": "high"},
 {"id": "axiom-bms-design", "title": "BMS Control Design", "domain": "automotive", "subdomain": "bms", "category": "design", "maturity": "experimental", "desc": "Designs cell modeling assumptions, SOC/SOH method selection, contactor/precharge, insulation monitoring and thermal strategy for battery systems.", "platforms": ["mcu"], "standards": ["ISO 26262:2018"], "artifacts": ["BMS design review", "fault-handling table"], "risk": "high"},
 {"id": "axiom-bms-diagnostics", "title": "BMS Diagnostics and HIL Test Design", "domain": "automotive", "subdomain": "bms", "category": "verification", "maturity": "experimental", "desc": "Designs BMS fault handling and HIL test campaigns covering cell, contactor, thermal and isolation faults.", "platforms": ["mcu"], "standards": ["ISO 26262:2018"], "artifacts": ["HIL test plan"], "risk": "high"},
 {"id": "axiom-v2x-communication", "title": "V2X Communication Design", "domain": "automotive", "subdomain": "v2x", "category": "design", "maturity": "experimental", "desc": "Models V2X messages, latency/security considerations and simulation hooks with a message test strategy.", "platforms": ["mpu"], "standards": ["ETSI ITS-G5"], "artifacts": ["message model", "test strategy"], "risk": "medium"},
 {"id": "axiom-zonal-architecture", "title": "Zonal Architecture Design", "domain": "automotive", "subdomain": "zonal", "category": "architecture", "maturity": "experimental", "desc": "Designs zonal/domain-controller partitioning, service-oriented communication, compute allocation and update strategy.", "platforms": ["mcu", "mpu", "soc"], "standards": ["AUTOSAR"], "artifacts": ["zonal architecture record"], "risk": "medium"},
 {"id": "axiom-automotive-release-readiness", "title": "Automotive Release Readiness", "domain": "automotive", "subdomain": "release", "category": "release", "maturity": "experimental", "desc": "Gates ECU/software release readiness with evidence packaging, open-finding triage and sign-off checklists.", "platforms": ["mcu", "mpu"], "standards": ["Automotive SPICE"], "artifacts": ["release gate report", "evidence package"], "risk": "high"},
 {"id": "axiom-embedded-firmware-bringup", "title": "Embedded Firmware Bring-up", "domain": "platform", "subdomain": "bringup", "category": "implementation", "maturity": "experimental", "desc": "Brings up firmware on a new MCU/board (clock, memory, drivers, bootloader handoff) with a deterministic checklist.", "platforms": ["mcu", "bare-metal"], "standards": [], "artifacts": ["bring-up checklist", "bring-up report"], "risk": "medium"},
 {"id": "axiom-rtos-architecture", "title": "RTOS Architecture Review", "domain": "platform", "subdomain": "rtos", "category": "architecture", "maturity": "experimental", "desc": "Reviews RTOS task, priority, IPC and timing architecture for determinism and stack safety.", "platforms": ["mcu", "rtos"], "standards": [], "artifacts": ["RTOS review"], "risk": "medium"},
 {"id": "axiom-trace-analysis", "title": "Trace Analysis", "domain": "platform", "subdomain": "observability", "category": "verification", "maturity": "experimental", "desc": "Analyzes execution traces for timing, dropped events and anomaly triage with a deterministic parser script.", "platforms": ["mcu", "mpu"], "standards": [], "artifacts": ["trace analysis report"], "risk": "low"},
 {"id": "axiom-memory-and-performance-analysis", "title": "Memory and Performance Analysis", "domain": "platform", "subdomain": "performance", "category": "verification", "maturity": "experimental", "desc": "Analyzes memory classification, stack/heap budgets and performance hotspots against project budgets.", "platforms": ["mcu", "mpu"], "standards": [], "artifacts": ["memory/perf report"], "risk": "medium"},
 {"id": "axiom-test-automation", "title": "Embedded Test Automation", "domain": "platform", "subdomain": "testing", "category": "verification", "maturity": "experimental", "desc": "Designs unit/integration test strategy, automation hooks and coverage expectations for embedded repos.", "platforms": ["mcu", "mpu"], "standards": [], "artifacts": ["test strategy", "test plan"], "risk": "low"},
 {"id": "axiom-hil-test-planning", "title": "HIL Test Planning", "domain": "platform", "subdomain": "testing", "category": "verification", "maturity": "experimental", "desc": "Plans SIL/HIL campaigns including plant models, fault injection and pass/fail criteria.", "platforms": ["mcu", "mpu"], "standards": [], "artifacts": ["HIL test plan"], "risk": "medium"},
 {"id": "axiom-robotics-system-integration", "title": "Robotics System Integration", "domain": "robotics", "subdomain": "integration", "category": "integration", "maturity": "experimental", "desc": "Integrates ROS 2 nodes, sensor fusion and motion-control interfaces with contract checks.", "platforms": ["mpu", "soc"], "standards": [], "artifacts": ["integration review"], "risk": "medium"},
 {"id": "axiom-industrial-control-review", "title": "Industrial Control Review", "domain": "industrial", "subdomain": "control", "category": "review", "maturity": "experimental", "desc": "Reviews PLC/fieldbus/OPC-UA control designs and functional-safety touchpoints for industrial controllers.", "platforms": ["mcu", "mpu"], "standards": ["IEC 61508"], "artifacts": ["control review"], "risk": "high"},
 {"id": "axiom-aerospace-defense-safety-review", "title": "Aerospace and Defense Safety Review", "domain": "aerospace", "subdomain": "safety", "category": "review", "maturity": "experimental", "desc": "Reviews safety-critical embedded designs against DO-178C/DO-254-style objectives and evidence expectations.", "platforms": ["mcu", "mpu"], "standards": ["DO-178C", "DO-254"], "artifacts": ["safety review"], "risk": "safety-critical"},
 {"id": "axiom-platform-architecture-review", "title": "Platform Architecture Review", "domain": "cross-domain", "subdomain": "architecture", "category": "architecture", "maturity": "experimental", "desc": "Reviews embedded platform architecture (requirements-to-design traceability, interface contracts, ADRs, tech-debt) for any domain.", "platforms": ["mcu", "mpu", "soc"], "standards": [], "artifacts": ["architecture review", "ADR set"], "risk": "medium"},
 # --- Track C additions (C2 automotive) ---
 {"id": "axiom-misra-c-cpp-review", "title": "MISRA C/C++ Review", "domain": "automotive", "subdomain": "coding-standards", "category": "review", "maturity": "experimental", "desc": "Reviews C/C++ code against MISRA C:2012 / MISRA C++:2023 guidelines with deviation handling.", "platforms": ["mcu", "mpu"], "standards": ["MISRA C:2012", "MISRA C++:2023"], "artifacts": ["MISRA review", "deviation record"], "risk": "high"},
 {"id": "axiom-bootloader-ota", "title": "Bootloader and OTA Design", "domain": "automotive", "subdomain": "update", "category": "design", "maturity": "experimental", "desc": "Designs secure bootloader, A/B update, rollback and OTA campaign strategy for ECUs.", "platforms": ["mcu", "mpu"], "standards": ["ISO 26262:2018", "UNECE R156"], "artifacts": ["bootloader design", "OTA plan"], "risk": "safety-critical"},
 {"id": "axiom-secoc-can-auth", "title": "SecOC CAN Authentication", "domain": "automotive", "subdomain": "cybersecurity", "category": "design", "maturity": "experimental", "desc": "Designs SecOC MAC/freshness-value schemes for authenticated CAN communication.", "platforms": ["mcu"], "standards": ["AUTOSAR SecOC", "ISO/SAE 21434"], "artifacts": ["SecOC design", "key-management notes"], "risk": "high"},
 {"id": "axiom-flexray-network", "title": "FlexRay Network Design", "domain": "automotive", "subdomain": "networks", "category": "design", "maturity": "experimental", "desc": "Designs FlexRay static/dynamic segments, cluster parameters and sync nodes.", "platforms": ["mcu"], "standards": ["FlexRay Protocol", "ISO 17458"], "artifacts": ["FlexRay design", "cluster config"], "risk": "high"},
 {"id": "axiom-lin-network", "title": "LIN Network Design", "domain": "automotive", "subdomain": "networks", "category": "design", "maturity": "experimental", "desc": "Designs LIN schedules, signal packing and master/slave configuration.", "platforms": ["mcu"], "standards": ["ISO 17987"], "artifacts": ["LIN design", "schedule table"], "risk": "medium"},
 {"id": "axiom-obd-ii-diagnostics", "title": "OBD-II Diagnostics", "domain": "automotive", "subdomain": "diagnostics", "category": "design", "maturity": "experimental", "desc": "Designs OBD-II PID support, readiness monitors and freeze-frame handling.", "platforms": ["mcu", "mpu"], "standards": ["SAE J1979", "ISO 15031"], "artifacts": ["OBD-II matrix"], "risk": "medium"},
 {"id": "axiom-xcp-calibration", "title": "XCP Calibration Protocol", "domain": "automotive", "subdomain": "calibration", "category": "design", "maturity": "experimental", "desc": "Designs XCP on CAN/Ethernet calibration sessions, DAQ lists and seed-key security.", "platforms": ["mcu", "mpu"], "standards": ["ASAM MCD-1 XCP"], "artifacts": ["XCP config", "calibration plan"], "risk": "medium"},
 {"id": "axiom-aspice-process", "title": "Automotive SPICE Process", "domain": "automotive", "subdomain": "process", "category": "process", "maturity": "experimental", "desc": "Maps project practices to Automotive SPICE process areas and base practices.", "platforms": ["mcu", "mpu"], "standards": ["Automotive SPICE"], "artifacts": ["ASPICE assessment"], "risk": "medium"},
 {"id": "axiom-iso-21434-tara", "title": "ISO 21434 TARA", "domain": "automotive", "subdomain": "cybersecurity", "category": "security", "maturity": "experimental", "desc": "Runs threat analysis and risk assessment aligned to ISO/SAE 21434.", "platforms": ["mcu", "mpu"], "standards": ["ISO/SAE 21434"], "artifacts": ["TARA report", "risk treatment"], "risk": "safety-critical"},
 {"id": "axiom-unece-r155-r156", "title": "UNECE R155/R156 Compliance", "domain": "automotive", "subdomain": "cybersecurity", "category": "compliance", "maturity": "experimental", "desc": "Maps cybersecurity-management and software-update systems to UNECE R155/R156.", "platforms": ["mcu", "mpu"], "standards": ["UNECE R155", "UNECE R156"], "artifacts": ["compliance matrix"], "risk": "high"},
 # --- C3 aerospace/defense ---
 {"id": "axiom-do178c-planning", "title": "DO-178C Planning", "domain": "aerospace", "subdomain": "certification", "category": "planning", "maturity": "experimental", "desc": "Plans DO-178C software lifecycle data and objectives for airborne software.", "platforms": ["mcu", "mpu"], "standards": ["DO-178C"], "artifacts": ["plan for software aspects"], "risk": "safety-critical"},
 {"id": "axiom-do254-hardware", "title": "DO-254 Hardware Assurance", "domain": "aerospace", "subdomain": "hardware", "category": "assurance", "maturity": "experimental", "desc": "Reviews complex electronic hardware assurance against DO-254 objectives.", "platforms": ["mcu", "fpga"], "standards": ["DO-254"], "artifacts": ["hardware assurance plan"], "risk": "safety-critical"},
 {"id": "axiom-arinc429-bus", "title": "ARINC 429 Bus Design", "domain": "aerospace", "subdomain": "avionics-bus", "category": "design", "maturity": "experimental", "desc": "Designs ARINC 429 word/label allocation and receive/transmit handling.", "platforms": ["mcu", "mpu"], "standards": ["ARINC 429"], "artifacts": ["bus design", "label table"], "risk": "high"},
 {"id": "axiom-arinc653-partition", "title": "ARINC 653 Partitioning", "domain": "aerospace", "subdomain": "rtos", "category": "architecture", "maturity": "experimental", "desc": "Designs ARINC 653 partitions, health monitoring and inter-partition communication.", "platforms": ["mpu"], "standards": ["ARINC 653"], "artifacts": ["partition plan"], "risk": "safety-critical"},
 {"id": "axiom-mil1553-bus", "title": "MIL-STD-1553 Bus", "domain": "defense", "subdomain": "avionics-bus", "category": "design", "maturity": "experimental", "desc": "Designs MIL-STD-1553 BC/RT/monitor terminal roles and message scheduling.", "platforms": ["mcu", "mpu"], "standards": ["MIL-STD-1553"], "artifacts": ["bus design", "message schedule"], "risk": "high"},
 {"id": "axiom-spacewire-link", "title": "SpaceWire Link Design", "domain": "aerospace", "subdomain": "space", "category": "design", "maturity": "experimental", "desc": "Designs SpaceWire links, routing and RMAP transactions for spacecraft.", "platforms": ["mpu", "soc"], "standards": ["ECSS-E-ST-50-12C"], "artifacts": ["link design"], "risk": "high"},
 {"id": "axiom-do326a-cyber", "title": "DO-326A Airworthiness Security", "domain": "aerospace", "subdomain": "cybersecurity", "category": "security", "maturity": "experimental", "desc": "Applies DO-326A airworthiness security process to airborne systems.", "platforms": ["mpu"], "standards": ["DO-326A", "DO-356A"], "artifacts": ["security assessment"], "risk": "safety-critical"},
 # --- C4 industrial ---
 {"id": "axiom-iec61508-safety", "title": "IEC 61508 Safety Lifecycle", "domain": "industrial", "subdomain": "safety", "category": "safety", "maturity": "experimental", "desc": "Supports IEC 61508 safety lifecycle, SIL determination and evidence.", "platforms": ["mcu", "mpu"], "standards": ["IEC 61508"], "artifacts": ["safety plan", "SIL allocation"], "risk": "safety-critical"},
 {"id": "axiom-iec61131-plc", "title": "IEC 61131-3 PLC Programming", "domain": "industrial", "subdomain": "plc", "category": "design", "maturity": "experimental", "desc": "Reviews PLC programming languages and scan-cycle design per IEC 61131-3.", "platforms": ["plc", "mpu"], "standards": ["IEC 61131-3"], "artifacts": ["PLC design review"], "risk": "medium"},
 {"id": "axiom-iec62443-security", "title": "IEC 62443 Industrial Security", "domain": "industrial", "subdomain": "cybersecurity", "category": "security", "maturity": "experimental", "desc": "Applies IEC 62443 zones/conduits and security levels to industrial controllers.", "platforms": ["mpu"], "standards": ["IEC 62443"], "artifacts": ["security concept", "zone model"], "risk": "high"},
 {"id": "axiom-modbus-protocol", "title": "Modbus Protocol Integration", "domain": "industrial", "subdomain": "fieldbus", "category": "integration", "maturity": "experimental", "desc": "Integrates Modbus RTU/TCP register maps and timing constraints.", "platforms": ["mcu", "mpu"], "standards": ["Modbus"], "artifacts": ["register map", "integration review"], "risk": "medium"},
 {"id": "axiom-opcua-server", "title": "OPC UA Server Design", "domain": "industrial", "subdomain": "opcua", "category": "design", "maturity": "experimental", "desc": "Designs OPC UA address space, security policies and subscription handling.", "platforms": ["mpu"], "standards": ["IEC 62541"], "artifacts": ["address space design"], "risk": "medium"},
 {"id": "axiom-ethercat-motion", "title": "EtherCAT Motion Integration", "domain": "industrial", "subdomain": "fieldbus", "category": "integration", "maturity": "experimental", "desc": "Integrates EtherCAT slaves, PDO mapping and distributed clocks.", "platforms": ["mcu", "mpu"], "standards": ["IEC 61158", "EtherCAT"], "artifacts": ["PDO map", "timing review"], "risk": "high"},
 {"id": "axiom-profinet-integration", "title": "PROFINET Integration", "domain": "industrial", "subdomain": "fieldbus", "category": "integration", "maturity": "experimental", "desc": "Integrates PROFINET IO devices, GSDML and real-time classes.", "platforms": ["mpu"], "standards": ["PROFINET"], "artifacts": ["integration review"], "risk": "medium"},
 # --- C5 robotics ---
 {"id": "axiom-ros2-node-design", "title": "ROS 2 Node Design", "domain": "robotics", "subdomain": "ros2", "category": "design", "maturity": "experimental", "desc": "Designs ROS 2 nodes, topics, services, actions and QoS profiles.", "platforms": ["mpu", "soc"], "standards": ["ROS 2"], "artifacts": ["node design", "interface contract"], "risk": "medium"},
 {"id": "axiom-microros-embedded", "title": "micro-ROS on MCU", "domain": "robotics", "subdomain": "microros", "category": "integration", "maturity": "experimental", "desc": "Integrates micro-ROS on MCUs with agent/transport and memory constraints.", "platforms": ["mcu"], "standards": ["micro-ROS"], "artifacts": ["integration review"], "risk": "medium"},
 {"id": "axiom-motion-control", "title": "Motion Control Design", "domain": "robotics", "subdomain": "motion", "category": "design", "maturity": "experimental", "desc": "Designs PID/cascade motion control, tuning and safety limits.", "platforms": ["mcu", "mpu"], "standards": [], "artifacts": ["control design", "tuning plan"], "risk": "high"},
 {"id": "axiom-robot-safety", "title": "Robot Safety (ISO 10218)", "domain": "robotics", "subdomain": "safety", "category": "safety", "maturity": "experimental", "desc": "Applies collaborative-robot safety per ISO 10218/TS 15066.", "platforms": ["mcu", "mpu"], "standards": ["ISO 10218", "ISO/TS 15066"], "artifacts": ["safety assessment"], "risk": "safety-critical"},
 # --- C6 general embedded ---
 {"id": "axiom-freertos-integration", "title": "FreeRTOS Integration", "domain": "platform", "subdomain": "rtos", "category": "integration", "maturity": "experimental", "desc": "Integrates FreeRTOS tasks, queues, mutexes and tick configuration.", "platforms": ["mcu"], "standards": [], "artifacts": ["RTOS config review"], "risk": "medium"},
 {"id": "axiom-zephyr-integration", "title": "Zephyr RTOS Integration", "domain": "platform", "subdomain": "rtos", "category": "integration", "maturity": "experimental", "desc": "Integrates Zephyr devicetree, Kconfig and west build.", "platforms": ["mcu"], "standards": [], "artifacts": ["Zephyr review"], "risk": "medium"},
 {"id": "axiom-threadx-integration", "title": "ThreadX RTOS Integration", "domain": "platform", "subdomain": "rtos", "category": "integration", "maturity": "experimental", "desc": "Integrates Azure RTOS ThreadX threads and synchronization.", "platforms": ["mcu"], "standards": [], "artifacts": ["ThreadX review"], "risk": "medium"},
 {"id": "axiom-embedded-linux-yocto", "title": "Embedded Linux / Yocto", "domain": "platform", "subdomain": "linux", "category": "integration", "maturity": "experimental", "desc": "Builds and reviews Yocto-based embedded Linux images and layers.", "platforms": ["mpu", "soc"], "standards": [], "artifacts": ["Yocto review", "image manifest"], "risk": "medium"},
 {"id": "axiom-bare-metal-stm32", "title": "Bare-Metal STM32", "domain": "platform", "subdomain": "mcu", "category": "implementation", "maturity": "experimental", "desc": "Bare-metal STM32 startup, clock, GPIO, UART, DMA and linker setup.", "platforms": ["mcu"], "standards": [], "artifacts": ["bring-up checklist"], "risk": "medium"},
 {"id": "axiom-bare-metal-nxp-s32", "title": "Bare-Metal NXP S32", "domain": "platform", "subdomain": "mcu", "category": "implementation", "maturity": "experimental", "desc": "Bare-metal NXP S32K/S32G startup and peripheral setup.", "platforms": ["mcu"], "standards": [], "artifacts": ["bring-up checklist"], "risk": "medium"},
 {"id": "axiom-startup-linker-scripts", "title": "Startup and Linker Scripts", "domain": "platform", "subdomain": "build", "category": "implementation", "maturity": "experimental", "desc": "Reviews startup code and linker scripts for memory layout correctness.", "platforms": ["mcu", "mpu"], "standards": [], "artifacts": ["linker review"], "risk": "high"},
 {"id": "axiom-dma-isr-lowpower", "title": "DMA, ISR and Low-Power Design", "domain": "platform", "subdomain": "power", "category": "design", "maturity": "experimental", "desc": "Designs DMA channels, ISR priorities and low-power modes.", "platforms": ["mcu"], "standards": [], "artifacts": ["power/DMA design"], "risk": "medium"},
 {"id": "axiom-rust-embedded", "title": "Rust Embedded", "domain": "platform", "subdomain": "rust", "category": "implementation", "maturity": "experimental", "desc": "Embedded Rust with cortex-m, RTIC and probe-rs tooling.", "platforms": ["mcu"], "standards": [], "artifacts": ["Rust project review"], "risk": "medium"},
 {"id": "axiom-mil-sil-hil-testing", "title": "MIL/SIL/HIL Testing", "domain": "platform", "subdomain": "testing", "category": "verification", "maturity": "experimental", "desc": "Plans model/SIL/HIL test campaigns and back-to-back comparison.", "platforms": ["mcu", "mpu"], "standards": [], "artifacts": ["test plan"], "risk": "medium"},
 {"id": "axiom-reqif-traceability", "title": "ReqIF Traceability", "domain": "cross-domain", "subdomain": "traceability", "category": "traceability", "maturity": "experimental", "desc": "Imports/exports ReqIF requirements and links to code/tests.", "platforms": ["mcu", "mpu"], "standards": ["ReqIF 1.2"], "artifacts": ["traceability matrix"], "risk": "medium"},
 {"id": "axiom-mcp-tool-backlog", "title": "MCP Tool Backlog Review", "domain": "cross-domain", "subdomain": "tooling", "category": "review", "maturity": "experimental", "desc": "Reviews pending MCP tool backlog and prioritizes implementation.", "platforms": ["mcu", "mpu"], "standards": [], "artifacts": ["backlog report"], "risk": "low"},
]

SKILL_MD = """---\n{name}\n---\n\n# Axiom {title}\n\n## Purpose\n{desc}\n\nScope: {subdomain} ({domain}). Maturity: {maturity}. This skill is original AxiomEmbedded content.\n\n## When to Use\n- The project needs the {title_lower} engineering workflow.\n- Inputs listed below are available.\n\n## When Not to Use\n- As a substitute for qualified safety/security certification review.\n- When the required inputs are absent (record the gap instead of inventing data).\n\n## Required Inputs\n- Repository path and target file list.\n- User objective and constraints.\n- Domain artifacts for {subdomain} (see skill references/).\n\n## Optional Inputs\n- Existing reports, prior run manifests, tool availability notes.\n\n## Prerequisites\n- `axiom doctor --skip-tests` green; relevant base skills loaded.\n\n## Execution Workflow\n1. Normalize the request into objective, scope, and constraints.\n2. Inspect repo context and existing {subdomain} artifacts.\n3. Select method/template from this skill.\n4. Generate or modify artifacts (dry-run first).\n5. Validate structurally and semantically (scripts/ + checklists/).\n6. Run applicable checks; record results.\n7. Produce traceability and review evidence.\n8. Summarize assumptions, risks, next actions.\n\n## Tool Invocations\n- `run_skill` with structured context; dry-run before writes.\n- `validate_skill` must pass before release use.\n- MCP tools: {mcp}.\n\n## Decision Rules\n- Prefer explicit configuration over invented defaults; flag every assumption.\n- Safety/security-relevant outputs require human review (review_required: true).\n\n## Workflow\nFollow Execution Workflow; record per-step evidence in the run manifest.\n\n## Deliverables\n- Run report under `.axiom/runs/<timestamp>/{sid}/`.\n- Skill-specific artifacts listed in catalog outputs.\n\n## Acceptance Criteria\n- `validate_skill` passes; checklist gates all green; traceability complete.\n\n## Acceptance\n- All checklist gates pass; findings carry severity + evidence + action.\n\n## Validation Procedure\n1. `python scripts/validate_skills.py --skill {sid}`.\n2. Review checklist gates.\n3. Human review for high/safety-critical risk levels.\n\n## Common Failure Modes\n- Missing inputs invented instead of flagged -> require explicit inputs.\n- Unreviewed safety/security output merged -> block at review gate.\n\n## Guardrails\n- No secrets in files; no unsafe shell; no unvalidated paths; no network calls.\n- Never claim certification or compliance from heuristic checks.\n\n## References\n- Authoritative standard identifiers listed in catalog; landing URLs only, no normative text.\n"""

MANIFEST = """id: {sid}\nversion: 1.2.0\ncontract_version: 1\ntype: reusable-skill\nsource_of_truth:\n  instructions: SKILL.md\n  contract: manifest.yaml\nfacets:\n  domains:\n  - {domain}\n  platforms:\n{plats}standards:\n{stds}axiom:\n  dotted_name: axiom.{domain}.{short}\n  maturity: {maturity}\n  category: {category}\n"""


def build() -> dict[str, pathlib.Path]:
    tmpl = (ROOT / "skills" / "_templates" / "SKILL.template.md").read_text()
    _ = tmpl
    written: dict[str, pathlib.Path] = {}
    for s in SKILLS:
        d = ROOT / "skills" / s["id"]
        d.mkdir(parents=True, exist_ok=True)
        fm = {"name": s["id"], "title": s["title"], "description": s["desc"],
              "version": "0.1.0", "author": "PRATIK PATIL", "license": "Apache-2.0",
              "domains": ["automotive" if s["domain"] == "automotive" else s["domain"] if s["domain"] != "cross-domain" else "all"],
              "platforms": s["platforms"]}
        if s["domain"] == "platform":
            fm["domains"] = ["all"]
        fm_lines = ["name: " + s["id"], "title: " + s["title"],
                    "description: >",
                    "  " + s["desc"],
                    "version: 0.1.0", "author: PRATIK PATIL",
                    "license: Apache-2.0",
                    "domains: [" + ", ".join(fm["domains"]) + "]",
                    "platforms: [" + ", ".join(s["platforms"]) + "]",
                    "axiom:",
                    "  dotted_name: axiom." + s["domain"] + "." + s["id"].replace("axiom-", "").replace("-", "."),
                    "  domain: " + s["domain"],
                    "  subdomain: " + s["subdomain"],
                    "  category: " + s["category"],
                    "  maturity: " + s["maturity"],
                    "  owner: axiom-embedded",
                    "  tags: [" + s["subdomain"] + "]",
                    "  related_skills: []",
                    "  lifecycle: [requirements, architecture, design, implementation, integration, verification, validation, release]",
                    "  standards: [" + ", ".join(s["standards"]) + "]",
                    "  artifact_types: [" + ", ".join(s["artifacts"]) + "]",
                    "  mcp_tools: [run_skill, validate_skill]",
                    "  risk_level: " + ("safety-critical" if s["risk"] == "safety-critical" else s["risk"]),
                    "  review_required: true",
                    "  safety_critical: " + ("true" if s["risk"] == "safety-critical" else "false"),
                    "  inputs: [repository path, target files, objective, constraints]",
                    "  outputs: [run report, run manifest]",
                    "  required_tools: [validate_skill]",
                    "  optional_tools: [run_skill]"]
        body = SKILL_MD.format(name="\n".join(fm_lines), title=s["title"],
                               desc=s["desc"], subdomain=s["subdomain"],
                               domain=s["domain"], maturity=s["maturity"],
                               title_lower=s["title"].lower(),
                               mcp="run_skill, validate_skill",
                               sid=s["id"])
        p = d / "SKILL.md"
        if not p.exists():
            p.write_text(body, encoding="utf-8")
            written[s["id"]] = p
        plats = "".join(f"  - {pl}\n" for pl in s["platforms"])
        stds = "".join(f"  - {st}\n" for st in s["standards"]) or "  []\n"
        mp = d / "manifest.yaml"
        if not mp.exists():
            short = s["id"].replace("axiom-", "").replace("-", "_")
            mp.write_text(MANIFEST.format(sid=s["id"], domain=fm["domains"][0],
                                          plats=plats, stds=stds,
                                          maturity=s["maturity"],
                                          category=s["category"], short=short),
                          encoding="utf-8")
        ck = d / "checklists" / "review.yaml"
        ck.parent.mkdir(exist_ok=True)
        if not ck.exists():
            ck.write_text("gates:\n  - id: scope\n    text: Scope, inputs, prerequisites recorded\n  - id: method\n    text: Workflow steps executed with evidence\n  - id: validation\n    text: Scripts + checklist gates green\n  - id: traceability\n    text: Links complete\n  - id: review\n    text: Human review done for safety/security output\n",
                          encoding="utf-8")
        (d / "references").mkdir(exist_ok=True)
        (d / "templates").mkdir(exist_ok=True)
        (d / "scripts").mkdir(exist_ok=True)
        (d / "tests").mkdir(exist_ok=True)
    # catalog.yaml
    cat = {"schema_version": "1.0",
           "skills": [{"id": s["id"], "name": "axiom." + s["domain"] + "." + s["id"].replace("axiom-", "").replace("-", "."),
                       "title": s["title"], "version": "0.1.0",
                       "domain": s["domain"], "subdomain": s["subdomain"],
                       "category": s["category"], "maturity": s["maturity"],
                       "owner": "axiom-embedded", "tags": [s["subdomain"]],
                       "inputs": ["repository path", "target files", "objective", "constraints"],
                       "outputs": ["run report", "run manifest"],
                       "dependencies": [], "related_skills": [],
                       "path": "skills/" + s["id"], "enabled": True} for s in SKILLS]}
    (ROOT / "skills" / "catalog.yaml").write_text(
        yaml.safe_dump(cat, sort_keys=False), encoding="utf-8")
    # registry.yaml (prompt2 shape)
    reg = {"version": 1,
           "skills": [{"name": "axiom." + s["domain"] + "." + s["id"].replace("axiom-", "").replace("-", "."),
                       "path": "skills/" + s["id"], "domain": s["domain"],
                       "maturity": s["maturity"]} for s in SKILLS]}
    (ROOT / "skills" / "registry.yaml").write_text(
        yaml.safe_dump(reg, sort_keys=False), encoding="utf-8")
    return written


def check() -> int:
    missing = []
    for s in SKILLS:
        for rel in ("SKILL.md", "manifest.yaml", "checklists/review.yaml"):
            if not (ROOT / "skills" / s["id"] / rel).exists():
                missing.append(f"skills/{s['id']}/{rel}")
    for f in ("skills/catalog.yaml", "skills/registry.yaml"):
        if not (ROOT / f).exists():
            missing.append(f)
    if missing:
        print("MISSING:")
        for m in missing:
            print(f"- {m}")
        return 1
    print(f"scaffold OK: {len(SKILLS)} skills")
    return 0


if __name__ == "__main__":
    if "--check" in sys.argv:
        raise SystemExit(check())
    w = build()
    print(f"scaffolded {len(w)} new SKILL.md files ({len(SKILLS)} total in catalog)")
