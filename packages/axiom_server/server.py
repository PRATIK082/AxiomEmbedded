"""AxiomEmbedded REST + A2A server (stdlib http.server only).

    GET  /v1/skills               all skill ids + descriptions
    GET  /v1/skills/{id}          one skill body + manifest
    GET  /v1/profiles             all profiles
    GET  /.well-known/agent.json  agent card (A2A discovery)
    POST /v1/engage               {"domain","platform"} -> engagement slice
    POST /v1/run                  {"request","domain","platform"} -> plan
    POST /v1/a2a/tasks            A2A task envelope {"id","intent":{...}} -> plan

Every handler delegates to packages.axiom_sdk — the single implementation.

Usage:
    python -m axiom_cli serve --port 8931
"""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from packages import axiom_sdk

AGENT_CARD = {
    "name": "axiom-embedded",
    "version": "1.2.0",
    "description": "Domain-neutral embedded engineering skills: engage by domain/platform, plan-then-execute.",
    "interfaces": ["mcp", "a2a", "rest", "cli", "sdk"],
    "skills_endpoint": "/v1/skills",
    "engage_endpoint": "/v1/engage",
}


def _send(handler: BaseHTTPRequestHandler, payload, status: int = 200) -> None:
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class Handler(BaseHTTPRequestHandler):
    server_version = "AxiomEmbedded/1.2.0"

    def log_message(self, *args):  # keep test output clean
        pass

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", 0) or 0)
        return json.loads(self.rfile.read(length).decode("utf-8") or "{}")

    def do_GET(self):  # noqa: N802
        if self.path in ("/", "/dashboard"):
            body = dashboard_html().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/v1/skills":
            _send(self, axiom_sdk.list_skills())
        elif self.path.startswith("/v1/skills/"):
            skill_id = self.path.rsplit("/", 1)[-1]
            try:
                _send(self, axiom_sdk.read_skill(skill_id))
            except FileNotFoundError:
                _send(self, {"error": f"unknown skill: {skill_id}"}, 404)
        elif self.path == "/v1/profiles":
            _send(self, axiom_sdk.list_profiles())
        elif self.path == "/.well-known/agent.json":
            _send(self, AGENT_CARD)
        else:
            _send(self, {"error": "not found"}, 404)

    def do_POST(self):  # noqa: N802
        try:
            data = self._read_json()
        except Exception:
            _send(self, {"error": "invalid JSON"}, 400)
            return
        if self.path == "/v1/engage":
            _send(self, axiom_sdk.engage_skills(data.get("domain"), data.get("platform")))
        elif self.path == "/v1/packs":
            _send(self, axiom_sdk.select_toolpacks(
                data.get("domain"), data.get("platform"), data.get("standards") or []))
        elif self.path == "/v1/compose":
            _send(self, axiom_sdk.compose_mindmap(
                data.get("prompt", ""), data.get("domain"), data.get("platform"),
                data.get("os"), data.get("language"), data.get("standards") or [],
                data.get("hardware"), data.get("technology")))
        elif self.path == "/v1/run":
            _send(self, axiom_sdk.run_plan(data.get("request", ""), data.get("domain"), data.get("platform")))
        elif self.path == "/v1/a2a/tasks":
            intent = data.get("intent", {})
            _send(
                self,
                {
                    "task_id": data.get("id", "task-1"),
                    "status": "planned",
                    "plan": axiom_sdk.run_plan(
                        intent.get("request", ""), intent.get("domain"), intent.get("platform")
                    ),
                },
            )
        else:
            _send(self, {"error": "not found"}, 404)


def dashboard_html() -> str:
    """Render the `/` status dashboard (Simple-UI slice 1).

    Single implementation behind ``axiom status`` (terminal) and the
    ``axiom serve`` landing page. All metrics are live repository data
    via :mod:`packages.axiom_ops`.
    """
    from packages.axiom_ops import get_status

    st = get_status()
    skills = st.get("skills", {})
    inv = st.get("inventory", {})
    attention = st.get("needs_attention", [])
    recommended = st.get("recommended_next_action", "")
    rows = "".join(
        f"<li><b>{a.get('id', '')}</b> [{a.get('severity', '')}] "
        f"{a.get('title', '')} — {a.get('action', '')}</li>"
        for a in attention
    ) or "<li>None — repository is healthy.</li>"
    return (
        "<!doctype html><html><head><meta charset='utf-8'>"
        "<title>AxiomEmbedded — status</title></head><body>"
        f"<h1>AxiomEmbedded</h1><p>State: {st.get('state', '')}</p>"
        f"<p>Skills: {skills.get('total', 0)} "
        f"(latest {skills.get('latest', '')})</p>"
        f"<p>Inventory: {inv}</p>"
        "<h2>Needs attention</h2><ul>" + rows + "</ul>"
        f"<h2>Recommended next action</h2><p>{recommended}</p>"
        "</body></html>"
    )


def serve(port: int = 8931) -> int:
    with ThreadingHTTPServer(("127.0.0.1", port), Handler) as httpd:
        print(f"axiom serve on 127.0.0.1:{port}")
        httpd.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(serve())
