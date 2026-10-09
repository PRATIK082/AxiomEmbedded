# SPDX-License-Identifier: Apache-2.0
"""Phase 1c: skills/agents are the single source of truth for client files."""

import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "sync_clients.py"


def test_sync_check_passes_on_clean_tree():
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--check"],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_generated_files_exist_and_are_stamped():
    for rel in ("opencode.json", ".mcp.json", ".claude-plugin/plugin.json",
                ".github/copilot-instructions.md", "GEMINI.md"):
        path = ROOT / rel
        assert path.exists(), rel
        assert "sync_clients.py" in path.read_text(encoding="utf-8"), rel


def test_opencode_json_has_mcp_and_instructions():
    data = json.loads((ROOT / "opencode.json").read_text(encoding="utf-8"))
    assert "AGENTS.md" in data["instructions"]
    # OpenCode v1 shape: strict {type: local, command: [...], enabled}
    # (verified via `opencode mcp list`); the {command, args} split lives
    # only in .mcp.json for generic MCP clients.
    entry = data["mcp"]["axiom-embedded"]
    assert entry["type"] == "local" and entry["enabled"] is True
    assert entry["command"][-3:] == ["-m", "axiom_cli", "mcp"]


def test_agent_and_skill_copies_mirror_sources(tmp_path):
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(ROOT)],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    for agent_dir in sorted((ROOT / "agents").iterdir()):
        if not agent_dir.is_dir() or not (agent_dir / "AGENT.md").exists():
            continue
        for client in (".opencode", ".claude"):
            copy = ROOT / client / "agents" / f"{agent_dir.name}.md"
            assert copy.exists(), str(copy)
            assert (agent_dir / "AGENT.md").read_text(encoding="utf-8") in copy.read_text(encoding="utf-8")
    for skill_dir in sorted((ROOT / "skills").iterdir()):
        if not skill_dir.is_dir() or not (skill_dir / "SKILL.md").exists():
            continue
        for client in (".opencode", ".claude"):
            copy = ROOT / client / "skills" / skill_dir.name / "SKILL.md"
            assert copy.exists(), str(copy)
            assert (skill_dir / "SKILL.md").read_text(encoding="utf-8") in copy.read_text(encoding="utf-8")


def test_check_detects_stale_output(tmp_path):
    import shutil

    mini = tmp_path / "mini"
    (mini / "skills").mkdir(parents=True)
    (mini / "agents").mkdir(parents=True)
    shutil.copytree(ROOT / "skills" / "embedded-c", mini / "skills" / "embedded-c")
    shutil.copytree(ROOT / "agents" / "implementation", mini / "agents" / "implementation")
    shutil.copy(ROOT / "VERSION", mini / "VERSION")
    gen = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(mini)],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert gen.returncode == 0, gen.stdout + gen.stderr
    stale_target = mini / "GEMINI.md"
    stale_target.write_text("stale", encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(mini), "--check"],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "GEMINI.md" in proc.stdout


def _frontmatter(path: pathlib.Path) -> dict:
    import yaml
    text = path.read_text(encoding="utf-8")
    assert "sync_clients.py" in text, path
    return yaml.safe_load(text.split("---")[1])


def test_opencode_agents_are_subagents_with_allowlists():
    import json
    for agent_dir in sorted((ROOT / "agents").iterdir()):
        manifest = agent_dir / "manifest.json"
        if not agent_dir.is_dir() or not manifest.exists():
            continue
        perms = json.loads(manifest.read_text(encoding="utf-8")).get("permissions", {})
        front = _frontmatter(ROOT / ".opencode" / "agents" / f"{agent_dir.name}.md")
        assert front["mode"] == "subagent", agent_dir.name
        assert front["permission"]["bash"] == {"*": "ask", "git push *": "deny"}
        if perms.get("filesystem") == "read-write":
            assert front["permission"]["edit"] == "allow", agent_dir.name
        else:
            assert front["permission"]["edit"] == "deny", agent_dir.name
        # Claude copies stay free of OpenCode-only frontmatter.
        claude_front = _frontmatter(ROOT / ".claude" / "agents" / f"{agent_dir.name}.md")
        assert set(claude_front) == {"name", "description"}, agent_dir.name


def test_opencode_commands_and_plugin():
    import sys as _sys
    _sys.path.insert(0, str(ROOT / "scripts"))
    import sync_clients
    expected = {c["id"] for c in sync_clients.COMMANDS}
    assert expected >= {"axiom-engage", "axiom-plan", "axiom-status", "axiom-fix",
                        "axiom-feature", "axiom-impact", "axiom-context", "axiom-research"}
    for cmd_id in expected:
        front = _frontmatter(ROOT / ".opencode" / "commands" / f"{cmd_id}.md")
        assert "description" in front, cmd_id
        assert "axiom-" in cmd_id  # never shadow OpenCode built-ins
    research = _frontmatter(ROOT / ".opencode" / "commands" / "axiom-research.md")
    assert research.get("subtask") is True and research.get("agent") == "explore"
    plugin = ROOT / ".opencode" / "plugins" / "axiom-policy.ts"
    assert plugin.exists()
    text = plugin.read_text(encoding="utf-8")
    assert "export const server" in text and "tool.execute.before" in text
    assert "experimental.session.compacting" in text
