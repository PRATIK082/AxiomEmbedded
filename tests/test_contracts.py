from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

def test_required_contract_files_exist():
    for rel in ["AGENTS.md", ".github/copilot-instructions.md", "opencode.json", "schemas/artifact.schema.json", "schemas/agent.schema.json", "integrations/mcp/server-manifest.json", "integrations/a2a/agent-card.json"]:
        assert (ROOT / rel).exists(), rel

def test_agent_registry_is_populated():
    data = json.loads((ROOT / "registries/agents.json").read_text())
    assert len(data["agents"]) >= 10

def test_domain_registry_is_broad():
    data = json.loads((ROOT / "registries/domains.json").read_text())
    assert {"automotive","aerospace","defense","industrial","robotics","generic-embedded"}.issubset(set(data["domains"]))


def test_no_vendored_AxiomEmbedded _tree():
    assert not (ROOT / "legacy").exists()
