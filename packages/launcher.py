# SPDX-License-Identifier: Apache-2.0
"""Launch OpenCode with an Axiom-owned isolated config (`axiom oc ...`).

Axiom is a domain layer, not a runtime: this module shells out to a
user-installed ``opencode`` binary (Phase 2 amendment). Compatibility
scope, the tested version, and the fail-closed doctor rule live in
docs/OPENCODE_COMPAT.md; this module enforces them.

Isolation model (verified against OpenCode v1 docs):

- ``OPENCODE_CONFIG`` points at an Axiom-generated ``opencode.json``
  under ``~/.axiom/opencode/`` (never the user's own config).
- ``OPENCODE_CONFIG_DIR`` points at Axiom content (``.opencode/`` with
  agents/commands/skills) when a content source is available.
- ``OPENCODE_CONFIG_CONTENT`` is left for operator runtime overrides.
- ``--no-isolate`` runs inside the user's own OpenCode setup instead.
"""

from __future__ import annotations

import json
import os
import pathlib
import re
import shutil
import subprocess

from packages.installer import find_content_source, opencode_mcp_entry

TESTED_MIN = (1, 18, 31)
TESTED_MAX = (1, 18, 35)  # newest v1 surveyed; bump with docs/OPENCODE_COMPAT.md
TESTED_LINE = "v1 (tested: 1.18.31; see docs/OPENCODE_COMPAT.md)"
OVERRIDE_ENV = "AXIOM_ALLOW_UNTESTED_OPENCODE"
CONFIG_SCHEMA = "https://opencode.ai/config.json"

_VERSION_RE = re.compile(r"(\d+)\.(\d+)\.(\d+)")


def find_opencode() -> str | None:
    """Absolute path of the ``opencode`` binary, or None when absent."""
    return shutil.which("opencode")


def parse_version(text: str) -> tuple[int, int, int] | None:
    """Parse ``1.18.31``-style versions from ``opencode --version`` output."""
    match = _VERSION_RE.search(text or "")
    if not match:
        return None
    return tuple(int(part) for part in match.groups())  # type: ignore[return-value]


def opencode_status(opencode_bin: str | None = None) -> dict:
    """Detect OpenCode and classify compatibility (fail closed on majors).

    Returns a JSON-serialisable dict with ``state`` in
    ``ok | warn | fail`` plus human-readable ``detail``.
    """
    binary = opencode_bin or find_opencode()
    if not binary:
        return {
            "state": "fail",
            "binary": None,
            "version": None,
            "detail": "opencode not found on PATH (install: https://opencode.ai/docs)",
        }
    try:
        proc = subprocess.run(
            [binary, "--version"], capture_output=True, text=True, timeout=30
        )
    except Exception as exc:
        return {"state": "fail", "binary": binary, "version": None,
                "detail": f"opencode --version failed: {exc}"}
    version = parse_version(proc.stdout + proc.stderr)
    if version is None:
        return {"state": "fail", "binary": binary, "version": None,
                "detail": "could not parse `opencode --version` output"}
    label = ".".join(str(p) for p in version)
    override = os.environ.get(OVERRIDE_ENV) == "1"
    if version[0] >= 2 and not override:
        return {
            "state": "fail",
            "binary": binary,
            "version": label,
            "detail": (f"opencode {label} is outside the tested line ({TESTED_LINE}). "
                       f"Axiom refuses to launch until v2 is surveyed; "
                       f"override with {OVERRIDE_ENV}=1 at your own risk."),
        }
    if version[0] >= 2 and override:
        return {"state": "warn", "binary": binary, "version": label,
                "detail": f"opencode {label} untested ({OVERRIDE_ENV}=1 accepted risk)."}
    if version < TESTED_MIN:
        return {"state": "warn", "binary": binary, "version": label,
                "detail": f"opencode {label} is older than the tested floor "
                          f"{'.'.join(str(p) for p in TESTED_MIN)}; behaviour may differ."}
    if version > TESTED_MAX:
        return {"state": "warn", "binary": binary, "version": label,
                "detail": f"opencode {label} is a newer v1 than surveyed "
                          f"({'.'.join(str(p) for p in TESTED_MAX)}); re-verify per docs/OPENCODE_COMPAT.md."}
    return {"state": "ok", "binary": binary, "version": label,
            "detail": f"opencode {label} within the tested line."}


def axiom_opencode_home(home: pathlib.Path | None = None) -> pathlib.Path:
    """Axiom-owned OpenCode state dir (default ``~/.axiom/opencode``)."""
    base = home if home is not None else pathlib.Path.home()
    return base / ".axiom" / "opencode"


def _axiom_mcp_entry() -> dict:
    """axiom_mcp as an OpenCode `mcp.<name>` local-server entry (shared rule)."""
    entry, _note = opencode_mcp_entry()
    return entry


def ensure_isolated_config(home: pathlib.Path | None = None, *,
                           model: str | None = None,
                           source: str | pathlib.Path | None = None) -> dict:
    """Write (idempotently) the Axiom-owned OpenCode config; return paths.

    Writes only under ``axiom_opencode_home()``. ``OPENCODE_CONFIG_DIR``
    points at Axiom content (``.opencode/``) when a content source with
    one is available; otherwise the launcher runs with config-file
    isolation only and says so honestly.
    """
    root = axiom_opencode_home(home)
    root.mkdir(parents=True, exist_ok=True)
    config: dict = {"$schema": CONFIG_SCHEMA}
    if model:
        config["model"] = model
    config["mcp"] = {"axiom": _axiom_mcp_entry()}
    config_file = root / "opencode.json"
    config_file.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")

    config_dir: str | None = None
    note = "config-file isolation only (no axiom content source with .opencode/)"
    try:
        content = find_content_source(source)
    except ValueError:
        content = None
    if content is not None and (content / ".opencode").is_dir():
        config_dir = str(content / ".opencode")
        note = f"axiom agents/commands/skills from {content}"
    return {"config_file": str(config_file), "config_dir": config_dir, "note": note}


def launch_env(*, config_file: str, config_dir: str | None) -> dict:
    """Environment overrides that isolate OpenCode from user config."""
    env = dict(os.environ)
    env["OPENCODE_CONFIG"] = config_file
    env.pop("OPENCODE_CONFIG_CONTENT", None)
    if config_dir:
        env["OPENCODE_CONFIG_DIR"] = config_dir
    else:
        env.pop("OPENCODE_CONFIG_DIR", None)
    return env


def build_command(verb: str, args: list[str], *,
                  model: str | None = None, agent: str | None = None,
                  directory: str | None = None, fmt: str | None = None,
                  title: str | None = None) -> list[str]:
    """Argv for ``opencode <verb>`` with Axiom passthrough flags."""
    argv = ["opencode"]
    # Launcher verbs are Axiom-side UX: `research` executes as a framed
    # `opencode run` session (OpenCode v1 has no `research` subcommand).
    op_verb = "run" if verb == "research" else verb
    if op_verb == "tui":
        if directory:
            argv.append(directory)
    else:
        argv.append(op_verb)
        argv.extend(args)
    if model:
        argv.extend(["--model", model])
    if agent:
        argv.extend(["--agent", agent])
    if op_verb == "run" and directory:
        argv.extend(["--dir", directory])
    if op_verb == "run" and fmt:
        argv.extend(["--format", fmt])
    if op_verb == "run" and title:
        argv.extend(["--title", title])
    return argv
    if model:
        argv.extend(["--model", model])
    if agent:
        argv.extend(["--agent", agent])
    if op_verb == "run" and directory:
        argv.extend(["--dir", directory])
    if op_verb == "run" and fmt:
        argv.extend(["--format", fmt])
    if op_verb == "run" and title:
        argv.extend(["--title", title])
    return argv


RESEARCH_PREAMBLE = (
    "Research only: investigate and report. Do not modify, create, or delete "
    "any files. End with a short findings summary plus source paths/URLs.\n\n"
)


def execute(verb: str, args: list[str], *, model: str | None = None,
            agent: str | None = None, directory: str | None = None,
            fmt: str | None = None, title: str | None = None,
            source: str | None = None, isolate: bool = True,
            dry_run: bool = False, home: pathlib.Path | None = None) -> int:
    """Run (or dry-run) an OpenCode invocation; returns the exit code."""
    status = opencode_status()
    if status["state"] == "fail":
        print(json.dumps({"status": "error", **status}, indent=2))
        return 1
    if status["state"] == "warn":
        print(json.dumps({"status": "warning", **status}, indent=2))

    if isolate:
        cfg = ensure_isolated_config(home, model=None, source=source)
        env = launch_env(config_file=cfg["config_file"], config_dir=cfg["config_dir"])
        isolation = {"isolated": True, **cfg}
    else:
        env = dict(os.environ)
        isolation = {"isolated": False, "note": "using the operator's own OpenCode config"}
    argv = build_command(verb, args, model=model, agent=agent,
                         directory=directory, fmt=fmt, title=title)
    if dry_run:
        print(json.dumps({
            "status": "dry-run",
            "argv": argv,
            "env": {k: v for k, v in env.items() if k.startswith("OPENCODE_")},
            **isolation,
            "opencode": status,
        }, indent=2))
        return 0
    proc = subprocess.run([status["binary"], *argv[1:]], env=env)
    return proc.returncode
