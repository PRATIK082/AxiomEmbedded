"""AxiomEmbedded MCP server (Model Context Protocol, stdio transport).

Stdlib-only JSON-RPC 2.0 over newline-delimited stdio — no `mcp` package
needed. Any MCP client (Claude Code, Cursor, VS Code Copilot, OpenCode,
Gemini CLI, custom harnesses) can spawn it::

    python -m axiom_cli mcp

Protocol: `initialize` -> capabilities, `tools/list`, `tools/call`.
"""

from __future__ import annotations

import json
import sys

from packages import axiom_sdk as sdk

SERVER_INFO = {"name": "axiom-embedded", "version": "1.0.0"}
PROTOCOL_VERSION = "2024-11-05"

TOOLS = [
    {
        "name": "engage",
        "description": "Select the skills, profiles and context files for a domain/platform slice.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "domain": {"type": "string", "description": "e.g. automotive, aerospace, robotics"},
                "platform": {"type": "string", "description": "e.g. mcu, mpu, soc, soc-linux"},
            },
        },
    },
    {
        "name": "run_plan",
        "description": "Build an opencode-style plan-then-execute plan for a request (host provides the model).",
        "inputSchema": {
            "type": "object",
            "required": ["request"],
            "properties": {
                "request": {"type": "string"},
                "domain": {"type": "string"},
                "platform": {"type": "string"},
            },
        },
    },
    {
        "name": "read_skill",
        "description": "Read the full SKILL.md body for one skill.",
        "inputSchema": {
            "type": "object",
            "required": ["skill_id"],
            "properties": {"skill_id": {"type": "string"}},
        },
    },
    {
        "name": "list_skills",
        "description": "List all 47 skill ids.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "list_profiles",
        "description": "List available engagement profiles.",
        "inputSchema": {"type": "object", "properties": {}},
    },
]


def _text(payload) -> dict:
    return {"content": [{"type": "text", "text": json.dumps(payload, indent=2)}]}


def dispatch(method: str, params: dict):
    if method == "initialize":
        return {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {"tools": {}},
            "serverInfo": SERVER_INFO,
        }
    if method == "tools/list":
        return {"tools": TOOLS}
    if method == "tools/call":
        name = params.get("name", "")
        args = params.get("arguments", {}) or {}
        if name == "engage":
            return _text(sdk.engage(args.get("domain"), args.get("platform")))
        if name == "run_plan":
            return _text(sdk.run_plan(args.get("request", ""), args.get("domain"), args.get("platform")))
        if name == "read_skill":
            try:
                return _text({"skill_id": args.get("skill_id"), "body": sdk.read_skill(args.get("skill_id", ""))})
            except KeyError as exc:
                return {"content": [{"type": "text", "text": str(exc)}], "isError": True}
        if name == "list_skills":
            return _text({"skills": sdk.list_skills()})
        if name == "list_profiles":
            return _text({"profiles": sdk.list_profiles()})
        return {"content": [{"type": "text", "text": f"unknown tool: {name}"}], "isError": True}
    return None


def serve() -> int:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        method = msg.get("method", "")
        if method.startswith("notifications/"):
            continue
        mid = msg.get("id")
        try:
            result = dispatch(method, msg.get("params", {}) or {})
        except Exception as exc:  # noqa: BLE001
            sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": mid, "error": {"code": -32603, "message": str(exc)}}) + "\n")
            sys.stdout.flush()
            continue
        if result is None:
            sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": f"unknown method: {method}"}}) + "\n")
        else:
            sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": mid, "result": result}) + "\n")
        sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(serve())
