from __future__ import annotations
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
TASKS = ROOT / "evaluation" / "tasks"

tasks = [
 ("EV-006","code-review","automotive","mcu","Review CAN-FD UDS diagnostic handler for MISRA compliance.",["code-review","axiom-diagnostics-uds"],["misra-c"],False),
 ("EV-007","safety","aerospace","mpu","DO-178C DAL-A flight control software assurance.",["axiom-aerospace-defense-safety-review"],[""],True),
 ("EV-008","implementation","industrial","mpu","Implement Modbus RTU server on STM32 with IEC 61508 SIL-2.",["axiom-iec61508-safety"],[""],False),
 ("EV-009","implementation","robotics","mpu","Design ROS2 node for motor control with micro-ROS.",["axiom-ros2-node-design","axiom-motion-control"],[""],False),
 ("EV-010","code-review","automotive","mcu","Review AUTOSAR Classic BSW configuration for ARXML compliance.",["axiom-autosar-classic-bsw-integration"],[""],False),
 ("EV-011","safety","automotive","mcu","ISO 26262 ASIL-D hazard analysis for brake controller.",["axiom-iso26262","axiom-hazard-analysis"],["iso26262"],False),
 ("EV-012","implementation","automotive","mcu","Implement SecOC CAN authentication for zone controller.",["axiom-secoc-can-auth"],[""],False),
 ("EV-013","implementation","aerospace","mpu","ARINC 653 partition scheduling for avionics.",["axiom-arinc653-partition"],[""],False),
 ("EV-014","implementation","industrial","mpu","OPC UA server for industrial gateway.",["axiom-opcua-server"],[""],False),
 ("EV-015","implementation","robotics","mpu","EtherCAT motion control integration.",["axiom-ethercat-motion"],[""],False),
 ("EV-016","code-review","automotive","mcu","MISRA C review of bootloader.",["axiom-misra-c-cpp-review","axiom-bootloader-ota"],["misra-c"],False),
 ("EV-017","implementation","automotive","mcu","FreeRTOS integration on STM32 with low power.",["axiom-freertos-integration","axiom-dma-isr-lowpower"],[""],False),
 ("EV-018","implementation","embedded","mpu","Zephyr RTOS bring-up on Nordic nRF52.",["axiom-zephyr-integration"],[""],False),
 ("EV-019","implementation","embedded","mpu","Rust embedded firmware for sensor node.",["axiom-rust-embedded"],[""],False),
 ("EV-020","implementation","automotive","mcu","Embedded Linux Yocto build for IVI.",["axiom-embedded-linux-yocto"],[""],False),
 ("EV-021","safety","automotive","mcu","UNECE R155/R156 cybersecurity management.",["axiom-unece-r155-r156"],[""],False),
 ("EV-022","safety","automotive","mcu","ISO 21434 TARA for connected vehicle.",["axiom-iso-21434-tara"],[""],False),
 ("EV-023","implementation","aerospace","mpu","DO-326A cybersecurity for avionics.",["axiom-do326a-cyber"],[""],False),
 ("EV-024","implementation","aerospace","mpu","MIL-STD-1553 bus interface.",["axiom-mil1553-bus"],[""],False),
 ("EV-025","implementation","aerospace","mpu","ARINC 429 bus driver.",["axiom-arinc429-bus"],[""],False),
 ("EV-026","implementation","space","mpu","SpaceWire link design.",["axiom-spacewire-link"],[""],False),
 ("EV-027","implementation","industrial","mpu","IEC 61131-3 PLC control.",["axiom-iec61131-plc"],[""],False),
 ("EV-028","implementation","industrial","mpu","PROFINET integration.",["axiom-profinet-integration"],[""],False),
 ("EV-029","implementation","industrial","mpu","Modbus protocol stack.",["axiom-modbus-protocol"],[""],False),
 ("EV-030","implementation","robotics","mpu","Robot safety per ISO 10218.",["axiom-robot-safety"],[""],False),
]

for tid, agent, domain, platform, prompt, skills, stds, clarifies in tasks:
    content = "# " + tid + "\n"
    content += "id: " + tid + "\n"
    content += "agent: " + agent + "\n"
    content += "domain: " + domain + "\n"
    content += "platform: " + platform + "\n"
    content += "prompt: " + prompt + "\n"
    content += "expect:\n"
    content += "  skills_contain: " + str(skills) + "\n"
    if stds and stds != [""]:
        content += "  standards_contain: " + str(stds) + "\n"
    if clarifies:
        content += "  clarifies: true\n"
    (TASKS / (tid + ".yaml")).write_text(content, encoding="utf-8")

print("wrote " + str(len(tasks)) + " tasks")
print("total:", len(list(TASKS.glob('EV-*.yaml'))))
