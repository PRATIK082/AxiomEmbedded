"""Minimal interactive Axiom chat REPL (G1)."""
from __future__ import annotations

import json
import sys
import uuid
from pathlib import Path

from packages.skills.engage import engage
from packages.agents.router import route, detect_domain
from packages.memory import MemoryStore


def _default_store() -> MemoryStore:
    return MemoryStore(Path(".axiom") / "chat_memory.db")


def chat_loop(domain: str | None = None, platform: str | None = None) -> int:
    print("Axiom chat (type 'exit' to quit, 'help' for commands)")
    cur_domain = domain
    cur_platform = platform
    store = _default_store()
    session_id = f"chat-{uuid.uuid4().hex[:8]}"
    store.start_session(session_id)
    while True:
        try:
            line = input("axiom> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            store.end_session(session_id, "interrupted")
            store.close()
            return 0
        if not line:
            continue
        if line.lower() in ("exit", "quit", ":q"):
            store.end_session(session_id, "normal exit")
            store.close()
            return 0
        if line.lower() == "help":
            print("commands: domain <d>, platform <p>, engage, route <request>, "
                  "run <request>, sessions, doctor, exit")
            continue
        if line.lower() == "sessions":
            print(json.dumps(store.list_sessions(), indent=2))
            continue
        if line.lower().startswith("domain "):
            cur_domain = line.split(" ", 1)[1].strip()
            print(f"domain={cur_domain}")
            continue
        if line.lower().startswith("platform "):
            cur_platform = line.split(" ", 1)[1].strip()
            print(f"platform={cur_platform}")
            continue
        if line.lower() == "engage":
            print(json.dumps(engage(cur_domain, cur_platform), indent=2))
            continue
        if line.lower().startswith("route "):
            req = line.split(" ", 1)[1]
            print(json.dumps(route(req), indent=2))
            continue
        if line.lower().startswith("run "):
            req = line.split(" ", 1)[1]
            d = cur_domain or detect_domain(req)
            sel = engage(d, cur_platform)
            print(json.dumps({"request": req, "domain": d, "route": route(req),
                              "skills": sel.get("skill_count", 0)}, indent=2))
            continue
        if line.lower() == "doctor":
            import subprocess
            subprocess.run([sys.executable, "-m", "axiom_cli", "doctor", "--skip-tests"])
            continue
        d = cur_domain or detect_domain(line)
        sel = engage(d, cur_platform)
        print(json.dumps({"request": line, "domain": d, "route": route(line),
                          "engaged_skills": sel.get("skill_count", 0)}, indent=2))


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="axiom chat")
    ap.add_argument("--domain", default=None)
    ap.add_argument("--platform", default=None)
    args = ap.parse_args(argv)
    return chat_loop(args.domain, args.platform)
