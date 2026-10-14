from __future__ import annotations

INTENT_MAP = {
    "bug": "debugging",
    "defect": "debugging",
    "feature": "implementation",
    "review": "code-review",
    "test": "test-engineering",
    "architecture": "software-architecture",
    "requirement": "requirements",
    "audit": "project-audit",
    "brownfield": "brownfield-recovery",
}

def route(text: str) -> str:
    lower = text.lower()
    for key, agent in INTENT_MAP.items():
        if key in lower:
            return agent
    return "engineering-manager"


# Prompt -> domain detection. Distinctive, low-collision keywords only:
# generic English words ("can", "cal", "body", "code") are excluded on
# purpose. Sources: the 11 automotive skills' descriptions in
# registries/skill-index.json. First match wins; None = no signal.
# Canonical keyword lists live in configs/domain-routing.yaml; the map below
# is the compiled fallback so detection works even when the YAML is absent.
DOMAIN_KEYWORDS = {
    "automotive": [
        "automotive", "asil", "hara", "sotif", "fusa", "v-model",
        "uds", "misra", "autosar", "aspice", "oem", "ecu", "obd",
        "doip", "adas", "ncap", "secoc", "flexray", "j1939",
        "some/ip", "canfd", "can-fd", "can-xl", "lin bus", "v2x",
        "tara", "qnx", "aaos", "aeb", "bcm", "peps",
        "21434", "26262", "21448", "r155", "r156",
    ],
    "defense": [
        "defense", "defence", "mil-std", "milstd", "itar", "cmmc",
        "mission-critical", "rugged", "anti-tamper", "tamper",
        "fips-140", "electronic-warfare", "radar", "sonar",
    ],
    "aerospace": [
        "aerospace", "avionics", "do-254", "arp4754", "arp4761",
        "flight-control", "fadec", "arinc", "dal-a", "dal-b", "dal-c",
    ],
    "industrial": [
        "industrial", "plc", "scada", "modbus", "profinet", "ethercat",
        "iec-61508", "iec-62443", "sil-2", "sil-3", "fieldbus", "opc-ua", "dcs",
    ],
    "robotics": [
        "robotics", "ros2", "ros-2", "rclcpp", "urdf", "nav2", "moveit",
        "cobot", "slam", "px4", "mavlink",
    ],
    "energy": [
        "bms", "cell-balancing", "thermal-runaway", "iec-62660", "ul-1973",
        "mppt", "inverter", "soh", "soc-estimation", "contactor",
    ],
    "iot": [
        "iot", "matter protocol", "thread protocol", "zigbee", "lora",
        "nb-iot", "coap", "mqtt-sn", "openthread",
    ],
    "generic-embedded": [
        "firmware", "microcontroller", "cortex-m", "freertos", "zephyr",
        "bare-metal", "bsp", "hal", "cmsis",
    ],
}


def _routing_keywords() -> dict | None:
    """Prefer configs/domain-routing.yaml when present (single source)."""
    try:
        import pathlib as _pl

        import yaml as _yaml

        path = _pl.Path(__file__).resolve().parents[2] / "configs" / "domain-routing.yaml"
        if not path.exists():
            return None
        data = _yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        out = {}
        for domain, spec in (data.get("domains") or {}).items():
            keywords = (spec or {}).get("detect_keywords") or []
            if keywords:
                out[domain] = [str(k).lower() for k in keywords]
        return out or None
    except Exception:
        return None


def detect_domain(text: str) -> str | None:
    """Return the best-guess domain for a free-text prompt, or None."""
    lower = (text or "").lower()
    keywords_map = _routing_keywords() or DOMAIN_KEYWORDS
    for domain, keywords in keywords_map.items():
        for key in keywords:
            if key and key in lower:
                return domain
    return None
