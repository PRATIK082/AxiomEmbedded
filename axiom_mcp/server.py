# SPDX-License-Identifier: Apache-2.0
"""AxiomEmbedded MCP server over stdio (newline-delimited JSON-RPC 2.0).

Every tool mirrors an ``axiom`` CLI command and delegates to the same
underlying implementation (``packages.*``), so CLI and MCP always agree.
Each tool carries a JSON Schema ``inputSchema`` plus a plain-language
description for model-driven clients.

Envelope (same as ``packages.axiom_mcp``):
    {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}
    {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
     "params": {"name": "engage", "arguments": {"domain": "automotive"}}}

Usage:
    python -m axiom_mcp            # stdio server (any MCP client)
    python -m axiom_cli mcp        # same server via the axiom launcher
"""

from __future__ import annotations

import json
import pathlib
import sys
import traceback

import yaml

from axiom_cli import __version__ as CLI_VERSION
from packages import axiom_sdk
from packages.axiom_ops import get_status, plan_feature, plan_fix
from packages.context.indexer import write_index
from packages.context.selector import ContextBudget, select_from_index
from packages.workflow.entry import starting_phase

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _is_source_checkout() -> bool:
    return (ROOT / "pyproject.toml").exists() or (ROOT / ".git").exists()

SCHEMA_OBJECT = {"type": "object"}


def _str_prop(description: str) -> dict:
    return {"type": "string", "description": description}


def _opt_str_prop(description: str) -> dict:
    return {"type": ["string", "null"], "description": description}


def _schema(properties: dict, required: list[str] | None = None) -> dict:
    schema: dict = {"type": "object", "properties": properties}
    if required:
        schema["required"] = required
    return schema


def _read_yaml(path: pathlib.Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


# ---------------------------------------------------------------------------
# Tool handlers (each returns JSON-serializable data; no printing, no exit)
# ---------------------------------------------------------------------------

def tool_version(_args: dict) -> dict:
    return {"axiom": CLI_VERSION}


def tool_doctor(_args: dict) -> dict:
    return {
        "axiom": CLI_VERSION,
        "python": sys.version.split()[0],
        "source_checkout": _is_source_checkout(),
        # The stdio tool reports install health only; the full pytest gate
        # stays in `axiom doctor` (CLI) and CI so tool calls stay fast.
        "tests": "not-run (use `axiom doctor` or CI)",
    }


def tool_analyze(args: dict) -> dict:
    target = pathlib.Path(args.get("path", ".")).resolve()
    output = target / ".axiom" / "index.json"
    count = write_index(target, output)
    return {"root": str(target), "files_indexed": count, "index": str(output)}


def tool_graph_build(args: dict) -> dict:
    target = pathlib.Path(args.get("path", ".")).resolve()
    output = args.get("output")
    out = pathlib.Path(output).resolve() if output else target / ".axiom" / "index.json"
    count = write_index(target, out)
    return {"root": str(target), "files_indexed": count, "index": str(out)}


def tool_context_select(args: dict) -> dict:
    roots = args["roots"]
    selected = select_from_index(
        args.get("index", ".axiom/index.json"),
        roots,
        ContextBudget(
            max_files=int(args.get("max_files", 24)),
            max_bytes=int(args.get("max_bytes", 500000)),
        ),
    )
    return {"roots": roots, "selected": selected}


def tool_impact(args: dict) -> dict:
    raw = args["path"]
    p = pathlib.Path(raw)
    data = _read_yaml(p) if p.suffix in {".yaml", ".yml"} else {}
    entry = data.get("entry", "brownfield") if data else "unknown"
    return {
        "project": data.get("id", p.stem) if data else p.stem,
        "mode": data.get("lifecycle", "unknown") if data else "unknown",
        "entry": data.get("entry", "unknown") if data else "unknown",
        "next_phase": starting_phase(entry),
    }


def tool_profile_validate(args: dict) -> dict:
    data = _read_yaml(pathlib.Path(args["path"]))
    required = ["id", "version", "domains", "capabilities"]
    missing = [k for k in required if k not in data]
    return {"valid": not missing, "missing": missing, "profile": data}


def tool_workflow_plan(args: dict) -> dict:
    data = _read_yaml(pathlib.Path(args["profile"]))
    entry = args.get("entry") or data.get("entry", "greenfield")
    return {
        "profile": data.get("id"),
        "entry": entry,
        "start_phase": starting_phase(entry),
        "lifecycle": data.get("lifecycle", "v-model"),
    }


def tool_route(args: dict) -> dict:
    from packages.agents.router import route

    return {"request": args["request"], "intent": route(args["request"])}


def tool_engage(args: dict) -> dict:
    return axiom_sdk.engage_skills(args.get("domain"), args.get("platform"))


def tool_packs(args: dict) -> dict:
    return axiom_sdk.select_toolpacks(
        args.get("domain"), args.get("platform"), args.get("standards") or [])


def tool_compose(args: dict) -> dict:
    return axiom_sdk.compose_mindmap(
        args.get("prompt", ""), args.get("domain"), args.get("platform"),
        args.get("os"), args.get("language"), args.get("standards") or [],
        args.get("hardware"), args.get("technology"))


def tool_run_plan(args: dict) -> dict:
    return axiom_sdk.run_plan(args.get("request", ""), args.get("domain"), args.get("platform"))


def tool_read_skill(args: dict) -> dict:
    return axiom_sdk.read_skill(args["skill_id"])


def tool_list_skills(_args: dict) -> dict:
    return {"skills": axiom_sdk.list_skills()}


def tool_list_profiles(_args: dict) -> dict:
    return {"profiles": axiom_sdk.list_profiles()}


def tool_status(_args: dict) -> dict:
    return get_status()


def tool_fix(args: dict) -> dict:
    return plan_fix(args["issue_id"], args.get("domain"), args.get("platform"))


def tool_feature(args: dict) -> dict:
    return plan_feature(args["feature_id"], args.get("domain"), args.get("platform"))


def tool_install(args: dict) -> dict:
    from packages.installer import find_content_source, install_client

    return install_client(
        args["client"],
        pathlib.Path(args.get("path", ".")).resolve(),
        pathlib.Path(args["home"]).expanduser() if args.get("home") else pathlib.Path.home(),
        find_content_source(args.get("source")),
        is_global=bool(args.get("global", False)),
    )


def tool_research(args: dict) -> dict:
    from packages.research import BACKENDS, DEFAULT_MAX_SUBQUESTIONS, run

    backend = args.get("backend", "auto")
    if backend not in BACKENDS:
        return {"status": "error",
                "message": f"unknown backend: {backend} (choose from {BACKENDS})"}
    try:
        max_sub = int(args.get("max_subquestions", DEFAULT_MAX_SUBQUESTIONS))
    except (TypeError, ValueError):
        max_sub = DEFAULT_MAX_SUBQUESTIONS
    return run(args.get("question", ""), backend=backend,
               max_subquestions=max_sub, model=args.get("model"))


def tool_search_skills(args: dict) -> dict:
    return axiom_sdk.search_skills(args.get("query", ""),
                                   args.get("domain"), args.get("standard"))


def tool_validate_skill(args: dict) -> dict:
    return axiom_sdk.validate_skill(args["skill_id"])


def tool_skill_manifest(args: dict) -> dict:
    return axiom_sdk.skill_manifest(args["skill_id"])


def tool_run_skill(args: dict) -> dict:
    return axiom_sdk.run_skill(
        args["skill_id"], args.get("repo_path", "."),
        args.get("target_files") or [], args.get("objective", ""),
        args.get("constraints", ""), args.get("output_dir"),
        bool(args.get("apply", False)))


def tool_create_skill(args: dict) -> dict:
    import re as _re
    import sys as _sys
    sys_path = str(ROOT / "scripts")
    if sys_path not in _sys.path:
        _sys.path.insert(0, sys_path)
    from create_skill import scaffold
    if not _re.match(r"^axiom-[a-z0-9]+(-[a-z0-9]+)+$", args["skill_id"]):
        return {"status": "error", "message": "bad skill id"}
    if args.get("apply"):
        plan = scaffold(args["skill_id"], args.get("title", args["skill_id"]),
                        args.get("domain", "automotive"), True)
        return {"status": "ok", "applied": True, "files": plan}
    return {"status": "dry-run",
            "files": [f"skills/{args['skill_id']}/SKILL.md",
                      f"skills/{args['skill_id']}/manifest.yaml",
                      f"skills/{args['skill_id']}/checklists/review.yaml"]}


def tool_skill_pipeline(args: dict) -> dict:
    return axiom_sdk.skill_pipeline(check=bool(args.get("check", True)))


def tool_analyze_repository(args: dict) -> dict:
    return axiom_sdk.analyze_repository(args.get("repo_path"))


def tool_generate_checklist(args: dict) -> dict:
    return axiom_sdk.generate_checklist(
        args["skill_id"], args.get("output_path"), args.get("repo_path"))


def tool_generate_test_plan(args: dict) -> dict:
    return axiom_sdk.generate_test_plan(
        args["skill_id"], args.get("output_path"), args.get("repo_path"))


def tool_generate_traceability_matrix(args: dict) -> dict:
    return axiom_sdk.generate_traceability_matrix(
        args["skill_id"], args.get("output_path"), args.get("repo_path"))


def tool_generate_report(args: dict) -> dict:
    return axiom_sdk.generate_report(
        args["skill_id"], args.get("run_dir"), args.get("output_path"),
        args.get("repo_path"))


def tool_review_configuration(args: dict) -> dict:
    return axiom_sdk.review_configuration(
        args["skill_id"], args.get("config_path", ""),
        args.get("repo_path"))


def tool_analyze_trace(args: dict) -> dict:
    return axiom_sdk.analyze_trace(
        args.get("trace_path", ""), args.get("repo_path"))


TOOLS: dict[str, dict] = {
    "version": {
        "description": "Axiom version (mirrors `axiom version`).",
        "inputSchema": _schema({}),
        "handler": tool_version,
    },
    "doctor": {
        "description": "Install health: axiom/python versions and checkout type (mirrors `axiom doctor`; skips the pytest gate for speed).",
        "inputSchema": _schema({}),
        "handler": tool_doctor,
    },
    "analyze": {
        "description": "Index a repository tree and write .axiom/index.json (mirrors `axiom analyze <path>`).",
        "inputSchema": _schema({"path": _str_prop("Repository root to index.")}),
        "handler": tool_analyze,
    },
    "graph_build": {
        "description": "Build the artifact/file graph index (mirrors `axiom graph build <path> [--output]`).",
        "inputSchema": _schema(
            {
                "path": _str_prop("Repository root to index."),
                "output": _opt_str_prop("Index output path (default <path>/.axiom/index.json)."),
            }
        ),
        "handler": tool_graph_build,
    },
    "context_select": {
        "description": "Select budgeted context files from an index for given roots (mirrors `axiom context select --root ...`).",
        "inputSchema": _schema(
            {
                "index": _str_prop("Path to the index JSON (default .axiom/index.json)."),
                "roots": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Artifact root paths to expand context from.",
                },
                "max_files": {"type": "integer", "description": "Maximum files to return."},
                "max_bytes": {"type": "integer", "description": "Maximum total bytes to return."},
            },
            required=["roots"],
        ),
        "handler": tool_context_select,
    },
    "impact": {
        "description": "Project impact summary: lifecycle mode, entry point, next phase (mirrors `axiom impact <project.yaml>`).",
        "inputSchema": _schema({"path": _str_prop("Path to project.yaml.")}, required=["path"]),
        "handler": tool_impact,
    },
    "profile_validate": {
        "description": "Validate a profile YAML has required keys (mirrors `axiom profile validate <path>`).",
        "inputSchema": _schema({"path": _str_prop("Path to the profile YAML.")}, required=["path"]),
        "handler": tool_profile_validate,
    },
    "workflow_plan": {
        "description": "Resolve the starting workflow phase for a profile+entry (mirrors `axiom workflow plan --profile ...`).",
        "inputSchema": _schema(
            {
                "profile": _str_prop("Path to the profile YAML."),
                "entry": _opt_str_prop("Lifecycle entry point override."),
            },
            required=["profile"],
        ),
        "handler": tool_workflow_plan,
    },
    "route": {
        "description": "Route a request to the responsible specialist agent (mirrors `axiom route <request>`).",
        "inputSchema": _schema({"request": _str_prop("Engineering request text.")}, required=["request"]),
        "handler": tool_route,
    },
    "engage": {
        "description": "Resolve which skills/profiles a domain+platform project needs (mirrors `axiom engage`).",
        "inputSchema": _schema(
            {
                "domain": _opt_str_prop("Engineering domain (e.g. automotive)."),
                "platform": _opt_str_prop("Compute platform (e.g. mcu)."),
            }
        ),
        "handler": tool_engage,
    },
    "packs": {
        "description": "Select plug-and-play tool/pip packs by domain+platform+standards (mirrors `axiom packs`).",
        "inputSchema": _schema(
            {
                "domain": _opt_str_prop("Engineering domain (e.g. automotive)."),
                "platform": _opt_str_prop("Compute platform (e.g. mcu)."),
                "standards": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Standard filters (e.g. ISO 14229-1).",
                },
            }
        ),
        "handler": tool_packs,
    },
    "compose": {
        "description": "Compose a skill mind-map DAG from a prompt + facet axes (mirrors `axiom compose`).",
        "inputSchema": _schema(
            {
                "prompt": _str_prop("User engineering request text."),
                "domain": _opt_str_prop("Engineering domain (e.g. automotive)."),
                "platform": _opt_str_prop("Compute platform (e.g. mcu)."),
                "os": _opt_str_prop("Operating system (e.g. autosar-classic)."),
                "language": _opt_str_prop("Implementation language (e.g. c)."),
                "standards": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Standard filters (e.g. ISO 14229-1).",
                },
                "hardware": _opt_str_prop("Hardware target (e.g. arm-cortex-m)."),
                "technology": _opt_str_prop("Compute technology (e.g. mcu)."),
            },
            required=["prompt"],
        ),
        "handler": tool_compose,
    },
    "run_plan": {
        "description": "Plan-then-execute plan for a request: intent, skill slice, phases, approvals (mirrors `axiom run`).",
        "inputSchema": _schema(
            {
                "request": _str_prop("Engineering task text."),
                "domain": _opt_str_prop("Engineering domain."),
                "platform": _opt_str_prop("Compute platform."),
            },
            required=["request"],
        ),
        "handler": tool_run_plan,
    },
    "read_skill": {
        "description": "Return a skill's SKILL.md body plus manifest.",
        "inputSchema": _schema({"skill_id": _str_prop("Skill id (directory under skills/).")}, required=["skill_id"]),
        "handler": tool_read_skill,
    },
    "list_skills": {
        "description": "All skill ids with discovery descriptions.",
        "inputSchema": _schema({}),
        "handler": tool_list_skills,
    },
    "list_profiles": {
        "description": "All profile ids with domains/platforms.",
        "inputSchema": _schema({}),
        "handler": tool_list_profiles,
    },
    "status": {
        "description": "Terminal-dashboard data: project health, skill freshness, needs-attention, next action (mirrors `axiom status --format json`).",
        "inputSchema": _schema({}),
        "handler": tool_status,
    },
    "fix": {
        "description": "Emit the 10-step fix-defect plan for an issue id (mirrors `axiom fix`).",
        "inputSchema": _schema(
            {
                "issue_id": _str_prop("Issue identifier."),
                "domain": _opt_str_prop("Engineering domain."),
                "platform": _opt_str_prop("Compute platform."),
            },
            required=["issue_id"],
        ),
        "handler": tool_fix,
    },
    "feature": {
        "description": "Emit the 9-step add-feature plan for a feature id (mirrors `axiom feature`).",
        "inputSchema": _schema(
            {
                "feature_id": _str_prop("Feature identifier."),
                "domain": _opt_str_prop("Engineering domain."),
                "platform": _opt_str_prop("Compute platform."),
            },
            required=["feature_id"],
        ),
        "handler": tool_feature,
    },
    "research": {
        "description": "Deep-research question pipeline (planner -> searchers -> verifier -> synthesizer with citations; mirrors `axiom research`).",
        "inputSchema": _schema(
            {
                "question": _str_prop("Research question."),
                "backend": {"type": ["string", "null"], "description": "auto|opencode|local|tavily|brave|searxng (default auto)."},
                "max_subquestions": {"type": ["integer", "null"], "description": "Max planner sub-questions (default 3)."},
                "model": _opt_str_prop("Model id for the opencode backend."),
            },
            required=["question"],
        ),
        "handler": tool_research,
    },
    "install": {
        "description": "Install the Axiom pack for a client into a project dir or user-global config (mirrors `axiom install --client`). Merges, never clobbers.",
        "inputSchema": _schema(
            {
                "client": {"type": "string", "description": "opencode|claude|codex|gemini|copilot."},
                "path": _str_prop("Target project dir (project scope)."),
                "global": {"type": "boolean", "description": "Install to user-global config instead."},
                "source": _opt_str_prop("Axiom content source dir override."),
                "home": _opt_str_prop("Home dir override (testing global installs)."),
            },
            required=["client"],
        ),
        "handler": tool_install,
    },
    "search_skills": {
        "description": "Search the skill catalog by query/domain/standard (skill discovery).",
        "inputSchema": _schema(
            {
                "query": _str_prop("Free-text query."),
                "domain": _opt_str_prop("Domain filter."),
                "standard": _opt_str_prop("Standard filter."),
            }
        ),
        "handler": tool_search_skills,
    },
    "validate_skill": {
        "description": "Validate one skill's SKILL.md contract (no writes).",
        "inputSchema": _schema(
            {"skill_id": _str_prop("Skill id (directory under skills/).")},
            required=["skill_id"],
        ),
        "handler": tool_validate_skill,
    },
    "skill_manifest": {
        "description": "Derived manifest.json export for a skill (generated from SKILL.md; single source of truth).",
        "inputSchema": _schema(
            {"skill_id": _str_prop("Skill id (directory under skills/).")},
            required=["skill_id"],
        ),
        "handler": tool_skill_manifest,
    },
    "run_skill": {
        "description": "Run a skill as a structured workflow; dry-run unless apply=true (writes only under output_dir/.axiom/runs).",
        "inputSchema": _schema(
            {
                "skill_id": _str_prop("Skill id."),
                "repo_path": _opt_str_prop("Repository path."),
                "target_files": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Repo-relative target files.",
                },
                "objective": _opt_str_prop("User objective."),
                "constraints": _opt_str_prop("Constraints."),
                "output_dir": _opt_str_prop("Output directory."),
                "apply": {"type": "boolean", "description": "Write artifacts (default false=dry-run)."},
            },
            required=["skill_id"],
        ),
        "handler": tool_run_skill,
    },
    "create_skill": {
        "description": "Scaffold a new axiom-* skill (dry-run unless apply=true; writes only under skills/).",
        "inputSchema": _schema(
            {
                "skill_id": _str_prop("New skill id (axiom-<domain>-<capability>)."),
                "title": _str_prop("Human-readable title."),
                "domain": _opt_str_prop("Domain."),
                "apply": {"type": "boolean", "description": "Write scaffold (default false=dry-run)."},
            },
            required=["skill_id", "title"],
        ),
        "handler": tool_create_skill,
    },
    "analyze_repository": {
        "description": "Deterministic artifact inventory of a repo (read-only; counts by artifact type).",
        "inputSchema": _schema(
            {"repo_path": _opt_str_prop("Repo-relative path (default: checkout root).")},
        ),
        "handler": tool_analyze_repository,
    },
    "generate_checklist": {
        "description": "Merge a skill's checklist gates into Markdown (dry-run unless output_path is set; writes confined to repo).",
        "inputSchema": _schema(
            {
                "skill_id": _str_prop("Skill id."),
                "output_path": _opt_str_prop("Repo-relative write target (omit for dry-run)."),
                "repo_path": _opt_str_prop("Repo root for confinement."),
            },
            required=["skill_id"],
        ),
        "handler": tool_generate_checklist,
    },
    "generate_test_plan": {
        "description": "Map a skill's Execution Workflow steps to verification activities (dry-run unless output_path is set).",
        "inputSchema": _schema(
            {
                "skill_id": _str_prop("Skill id."),
                "output_path": _opt_str_prop("Repo-relative write target (omit for dry-run)."),
                "repo_path": _opt_str_prop("Repo root for confinement."),
            },
            required=["skill_id"],
        ),
        "handler": tool_generate_test_plan,
    },
    "generate_traceability_matrix": {
        "description": "Emit Step x Inputs/Outputs/Evidence/Status CSV for a skill (dry-run unless output_path is set).",
        "inputSchema": _schema(
            {
                "skill_id": _str_prop("Skill id."),
                "output_path": _opt_str_prop("Repo-relative write target (omit for dry-run)."),
                "repo_path": _opt_str_prop("Repo root for confinement."),
            },
            required=["skill_id"],
        ),
        "handler": tool_generate_traceability_matrix,
    },
    "generate_report": {
        "description": "Render a run manifest (or skill context) as Markdown (dry-run unless output_path is set).",
        "inputSchema": _schema(
            {
                "skill_id": _str_prop("Skill id."),
                "run_dir": _opt_str_prop("Repo-relative run-manifest dir or file."),
                "output_path": _opt_str_prop("Repo-relative write target (omit for dry-run)."),
                "repo_path": _opt_str_prop("Repo root for confinement."),
            },
            required=["skill_id"],
        ),
        "handler": tool_generate_report,
    },
    "review_configuration": {
        "description": "Deterministic structural review of a config file (read-only; YAML/JSON parse, secret scan with line numbers only).",
        "inputSchema": _schema(
            {
                "skill_id": _str_prop("Skill id whose gates apply."),
                "config_path": _str_prop("Repo-relative config file."),
                "repo_path": _opt_str_prop("Repo root for confinement."),
            },
            required=["skill_id", "config_path"],
        ),
        "handler": tool_review_configuration,
    },
    "analyze_trace": {
        "description": "Deterministic trace summary: CSV/TSV histograms and time-range, or log keyword counts (read-only, capped).",
        "inputSchema": _schema(
            {
                "trace_path": _str_prop("Repo-relative trace file."),
                "repo_path": _opt_str_prop("Repo root for confinement."),
            },
            required=["trace_path"],
        ),
        "handler": tool_analyze_trace,
    },
    "skill_pipeline": {
        "description": "One-command skill pipeline (link->enrich->index->clients->validate); check-only unless apply=true.",
        "inputSchema": _schema(
            {
                "check": {"type": "boolean", "description": "Verify only (default true)."},
                "apply": {"type": "boolean", "description": "Write canonical generated files (default false)."},
            },
        ),
        "handler": lambda args: tool_skill_pipeline(
            {"check": not args.get("apply", False)}),
    },
}


def _public_tools() -> list[dict]:
    return [
        {"name": name, "description": spec["description"], "inputSchema": spec["inputSchema"]}
        for name, spec in TOOLS.items()
    ]


def dispatch(method: str, params: dict):
    if method == "initialize":
        # MCP handshake shape (strictly validated by clients like OpenCode):
        # echo the client's protocol version when offered.
        return {
            "protocolVersion": params.get("protocolVersion", "2024-11-05"),
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": "axiom-mcp", "version": CLI_VERSION},
        }
    if method == "notifications/initialized":
        return {}
    if method == "tools/list":
        return {"tools": _public_tools()}
    if method == "tools/call":
        name, args = params["name"], params.get("arguments", {})
        try:
            spec = TOOLS[name]
        except KeyError:
            raise ValueError(f"unknown tool: {name}") from None
        return spec["handler"](args or {})
    raise ValueError(f"unknown method: {method}")


def serve(stdin=None, stdout=None) -> int:
    stdin, stdout = stdin or sys.stdin, stdout or sys.stdout
    for line in stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            result = dispatch(req.get("method", ""), req.get("params", {}))
            resp = {"jsonrpc": "2.0", "id": req.get("id"), "result": result}
        except Exception as exc:  # noqa: BLE001 — errors cross the stdio boundary as responses
            resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32603, "message": str(exc), "data": traceback.format_exc(limit=3)},
            }
        # default=str: YAML manifests may carry dates; the stdio boundary must
        # always emit valid JSON rather than fail the whole response.
        stdout.write(json.dumps(resp, default=str) + "\n")
        stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(serve())
