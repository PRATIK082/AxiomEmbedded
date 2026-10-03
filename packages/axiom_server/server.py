"""AxiomEmbedded HTTP server: REST + A2A on one stdlib port.

Endpoints::

    GET  /v1/skills                list skill ids
    GET  /v1/skills/{id}           full SKILL.md body
    POST /v1/engage                 {domain?, platform?} -> engagement slice
    POST /v1/run                    {request, domain?, platform?} -> run plan
    GET  /v1/profiles              engagement profiles
    GET  /.well-known/agent.json    A2A agent card (discovery)
    POST /v1/a2a/tasks              A2A task envelope {message|request, domain?, platform?}

Run with ``python -m axiom_cli serve --port 8765``. Web apps, custom AI,
local LLMs, and A2A peers talk here; the SDK remains the single
implementation behind every route.
"""

from __future__ import annotations

import json
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from packages import axiom_sdk as sdk

AGENT_CARD = {
    "name": "axiom-embedded",
    "version": "1.0.0",
    "protocol": "a2a/axiom-rest-v1",
    "description": "Domain-neutral embedded engineering platform: skill engagement and plan-then-execute planning.",
    "capabilities": ["skill-engagement", "run-planning", "skill-reading", "profile-listing"],
    "interfaces": ["mcp-stdio", "rest", "a2a-task", "cli", "python-sdk"],
}


def _send(handler: BaseHTTPRequestHandler, status: int, payload) -> None:
    if isinstance(payload, str):
        body, ctype = payload.encode("utf-8"), "text/markdown; charset=utf-8"
    else:
        body, ctype = json.dumps(payload, indent=2).encode("utf-8"), "application/json"
    handler.send_response(status)
    handler.send_header("Content-Type", ctype)
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class Handler(BaseHTTPRequestHandler):
    server_version = "AxiomEmbedded/1.0"

    def log_message(self, *args):  # quieter logs
        pass

    def _body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0) or 0)
        if not length:
            return {}
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return {}

    def do_GET(self):  # noqa: N802
        if self.path == "/v1/skills":
            _send(self, 200, {"skills": sdk.list_skills()})
        elif self.path.startswith("/v1/skills/"):
            sid = self.path.rsplit("/", 1)[-1]
            try:
                _send(self, 200, {"skill_id": sid, "body": sdk.read_skill(sid)})
            except KeyError:
                _send(self, 404, {"error": f"unknown skill: {sid}"})
        elif self.path == "/v1/profiles":
            _send(self, 200, {"profiles": sdk.list_profiles()})
        elif self.path == "/.well-known/agent.json":
            _send(self, 200, AGENT_CARD)
        else:
            _send(self, 404, {"error": "not found"})

    def do_POST(self):  # noqa: N802
        data = self._body()
        if self.path == "/v1/engage":
            _send(self, 200, sdk.engage(data.get("domain"), data.get("platform")))
        elif self.path == "/v1/run":
            if not data.get("request"):
                _send(self, 400, {"error": "missing 'request'"})
            else:
                _send(self, 200, sdk.run_plan(data["request"], data.get("domain"), data.get("platform")))
        elif self.path == "/v1/a2a/tasks":
            request = data.get("message") or data.get("request", "")
            plan = sdk.run_plan(request, data.get("domain"), data.get("platform"))
            _send(self, 200, {
                "taskId": f"axiom-{uuid.uuid4().hex[:12]}",
                "status": "completed",
                "agent": AGENT_CARD["name"],
                "artifact": plan,
            })
        else:
            _send(self, 404, {"error": "not found"})


def create_server(port: int = 8765) -> ThreadingHTTPServer:
    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def serve(port: int = 8765) -> int:
    server = create_server(port)
    print(f"AxiomEmbedded serving REST+A2A on 127.0.0.1:{server.server_port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    import sys

    raise SystemExit(serve(int(sys.argv[1]) if len(sys.argv) > 1 else 8765))
