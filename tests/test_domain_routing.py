"""Domain routing: every agent resolves project context and binds domain skills."""
import json
import pathlib

import yaml

from packages.agents.project_context import resolve_project_context
from packages.agents.router import detect_domain

ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_detect_all_domains():
    assert detect_domain("ASIL-D ECU with UDS diagnostics") == "automotive"
    assert detect_domain("MIL-STD rugged mission-critical radar with tamper protection") == "defense"
    assert detect_domain("avionics DAL-B flight-control per ARINC") == "aerospace"
    assert detect_domain("PLC modbus scada SIL-2 loop") == "industrial"
    assert detect_domain("ROS2 nav2 slam cobot") == "robotics"
    assert detect_domain("BMS cell-balancing thermal-runaway inverter") == "energy"
    assert detect_domain("firmware cortex-m freertos bsp hal") == "generic-embedded"


def test_no_false_positives():
    assert detect_domain("can you fix the login bug") is None
    assert detect_domain("review this code for checksums") is None


def test_explicit_project_file_wins(tmp_path):
    (tmp_path / "axiom.project.yaml").write_text(
        "domain: defense\nplatform: mpu\nprofile: defense-embedded\nstandards: [iec-61508]\n",
        encoding="utf-8",
    )
    ctx = resolve_project_context(tmp_path, "automotive ECU request")
    assert ctx["domain"] == "defense"
    assert ctx["profile"] == "defense-embedded"
    assert ctx["source"].startswith("explicit:")


def test_fallback_generic(tmp_path):
    ctx = resolve_project_context(tmp_path, "can you fix the login bug")
    assert ctx["domain"] == "generic-embedded"


def test_routing_config_covers_facets():
    routing = yaml.safe_load((ROOT / "configs" / "domain-routing.yaml").read_text(encoding="utf-8"))
    facets = yaml.safe_load((ROOT / "registries" / "skill-facets.yaml").read_text(encoding="utf-8"))
    assert set(routing["domains"]) >= {"automotive", "defense", "aerospace", "industrial", "robotics", "energy", "generic-embedded", "iot"}
    for domain in routing["domains"]:
        assert "default_profile" in routing["domains"][domain]
        assert "priority_skills" in routing["domains"][domain]


def test_agent_manifests_domain_aware():
    for manifest in (ROOT / "agents").glob("*/manifest.json"):
        data = json.loads(manifest.read_text(encoding="utf-8"))
        assert data.get("domain_aware") is True, manifest
        assert data.get("requires_project_context") is True, manifest


def test_matrix_generated_and_fresh():
    import subprocess
    import sys

    proc = subprocess.run([sys.executable, "scripts/generate_agent_domain_matrix.py", "--check"],
                          capture_output=True, text=True, cwd=ROOT)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    matrix = json.loads((ROOT / "registries" / "agent-domain-matrix.json").read_text(encoding="utf-8"))
    assert "code-review" in matrix["matrix"]
    assert matrix["matrix"]["code-review"]["automotive"]["skill_count"] > 0
    assert matrix["matrix"]["code-review"]["defense"]["skill_count"] > 0


def test_repo_prompt_conflict_asks_and_unions(tmp_path):
    (tmp_path / "README.md").write_text("AUTOSAR ECU arxml aspice", encoding="utf-8")
    ctx = resolve_project_context(tmp_path, "MIL-STD rugged radar tamper", agent_id="code-review")
    assert ctx["domain"] == "automotive"
    assert ctx["prompt_domain"] == "defense"
    assert ctx["needs_clarification"] is True
    assert ctx["clarification_question"]
    primary = ctx["load_plan"]["primary"]
    assert "code-review" in primary  # core first
    assert len(primary) <= 8  # token cap honored


def test_fallback_asks_user(tmp_path):
    ctx = resolve_project_context(tmp_path, "can you fix the login bug", agent_id="safety")
    assert ctx["domain"] == "generic-embedded"
    assert ctx["needs_clarification"] is True
    assert ctx["confidence"] < 0.5


def test_prompt_extras_union_into_primary(tmp_path):
    ctx = resolve_project_context(tmp_path, "ROS2 nav2 slam cobot", agent_id="safety")
    assert ctx["domain"] in ("robotics", "generic-embedded")
    assert ctx["load_plan"]["core"] == "safety"
    assert len(ctx["load_plan"]["primary"]) <= 8


def test_agents_are_specific_not_generic():
    for agent_dir in (ROOT / "agents").iterdir():
        md = agent_dir / "AGENT.md"
        if not md.exists():
            continue
        text = md.read_text(encoding="utf-8")
        assert "Core skill for THIS agent" in text, agent_dir.name
        assert "Trigger table for " + agent_dir.name in text, agent_dir.name
        assert "needs_clarification" in text, agent_dir.name
    for manifest in (ROOT / "agents").glob("*/manifest.json"):
        data = json.loads(manifest.read_text(encoding="utf-8"))
        assert data["skill_binding"].get("core_skill"), manifest
        assert data.get("output_contract"), manifest
