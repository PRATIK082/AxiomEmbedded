"""AxiomEmbedded MCP server over stdio (newline-delimited JSON-RPC 2.0).

Tools: engage, run_plan, read_skill, list_skills, list_profiles.
Every tool delegates to packages.axiom_sdk — the single implementation.

Usage (опрос via clients/mcp.json):
    python -m packages.axiom_mcp.server
"""

from __future__ import annotations

import json
import sys
import traceback

from packages import axiom_sdk

TOOLS = {
    "engage": {
        "description": "Resolve which skills/profiles a domain+platform project needs.",
        "params": ["domain", "platform"],
    },
    "run_plan": {
        "description": "Opencode-like plan-then-execute plan for a request.",
        "params": ["request", "domain", "platform"],
    },
    "read_skill": {
        "description": "Return a skill's SKILL.md body plus manifest.",
        "params": ["skill_id"],
    },
    "list_skills": {"description": "All skill ids with descriptions.", "params": []},
    "list_profiles": {"description": "All profile ids with domains/platforms.", "params": []},
}


def dispatch(method: str, params: dict):
    if method == "tools/list":
        return {"tools": [{"name": n, **spec} for n, spec in TOOLS.items()]}
    if method == "tools/call":
        name, args = params["name"], params.get("arguments", {})
        if name == "engage":
            return axiom_sdk.engage_skills(args.get("domain"), args.get("platform"))
        if name == "run_plan":
            return axiom_sdk.run_plan(args.get("request", ""), args.get("domain"), args.get("platform"))
        if name == "read_skill":
            return axiom_sdk.read_skill(args["skill_id"])
        if name == "list_skills":
            return axiom_sdk.list_skills()
        if name == "list_profiles":
            return axiom_sdk.list_profiles()
        raise ValueError(f"unknown tool: {name}")
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
        stdout.write(json.dumps(resp) + "\n")
        stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(serve())
