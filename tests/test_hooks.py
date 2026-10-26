import json
import pathlib
import tempfile

from packages.hooks import HookEvent, load_hooks, run_hooks


def test_hook_event_values():
    assert "PreToolUse" in HookEvent.all()
    assert "PostToolUse" in HookEvent.all()


def test_load_hooks_empty():
    with tempfile.TemporaryDirectory() as d:
        assert load_hooks(pathlib.Path(d)) == {}


def test_run_hooks_no_hooks():
    with tempfile.TemporaryDirectory() as d:
        res = run_hooks("PreToolUse", {"tool": "x"}, root=pathlib.Path(d))
        assert res["passed"] is True
        assert res["hook_count"] == 0
        assert res["blocked"] is False


def test_run_hooks_executes_command():
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        (root / ".axiom").mkdir()
        (root / ".axiom" / "hooks.yaml").write_text(
            "hooks:\n"
            "  - name: echo-hook\n"
            "    event: PreToolUse\n"
            "    command: \"echo ok\"\n"
            "    enabled: true\n",
            encoding="utf-8",
        )
        res = run_hooks("PreToolUse", {}, root=root)
        assert res["hook_count"] == 1
        assert res["results"][0]["passed"] is True


def test_fail_closed_blocks():
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        (root / ".axiom").mkdir()
        (root / ".axiom" / "hooks.yaml").write_text(
            "hooks:\n"
            "  - name: fail-hook\n"
            "    event: PreToolUse\n"
            "    command: \"exit 1\"\n",
            encoding="utf-8",
        )
        res = run_hooks("PreToolUse", {}, root=root)
        assert res["blocked"] is True
        assert res["passed"] is False


def test_fail_open_does_not_block():
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        (root / ".axiom").mkdir()
        (root / ".axiom" / "hooks.yaml").write_text(
            "hooks:\n"
            "  - name: fail-hook\n"
            "    event: PostToolUse\n"
            "    command: \"exit 1\"\n",
            encoding="utf-8",
        )
        res = run_hooks("PostToolUse", {}, root=root)
        assert res["blocked"] is False
