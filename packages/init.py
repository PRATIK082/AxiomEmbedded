"""Project initialization wizard for AxiomEmbedded.

Interactive (and non-interactive via flags) scaffolding of a new project:
- prompts for domain profile, toolchain, model endpoint, storage path
- writes .axiom/project.yaml
- engages skills for the chosen domain
- optionally writes client config via `axiom install`
"""
from __future__ import annotations

import json
import pathlib
import sys
from datetime import datetime, timezone

PROFILES = ["automotive", "aerospace", "defense", "industrial", "robotics", "medical", "generic-embedded"]


def _ask(prompt: str, default: str | None = None, choices: list[str] | None = None) -> str:
    suffix = ""
    if choices:
        suffix = " [" + "/".join(choices) + "]"
    if default is not None:
        suffix += f" (default: {default})"
    while True:
        try:
            raw = input(f"{prompt}{suffix}: ").strip()
        except EOFError:
            raw = ""
        if not raw and default is not None:
            return default
        if not raw:
            print("  (required)")
            continue
        if choices and raw not in choices:
            print(f"  choose one of {choices}")
            continue
        return raw


def init_project(target: str | pathlib.Path, domain: str | None = None,
                 platform: str | None = None, model: str | None = None,
                 storage: str | None = None, non_interactive: bool = False) -> dict:
    target = pathlib.Path(target).resolve()
    target.mkdir(parents=True, exist_ok=True)
    axdir = target / ".axiom"
    axdir.mkdir(parents=True, exist_ok=True)

    if non_interactive:
        domain = domain or "generic-embedded"
        platform = platform or "stm32"
        model = model or "local"
        storage = storage or str(axdir)
    else:
        print("AxiomEmbedded project init")
        domain = domain or _ask("Domain profile", "generic-embedded", PROFILES)
        platform = platform or _ask("Target platform", "stm32")
        model = model or _ask("Model endpoint", "local")
        storage = storage or _ask("Storage path", str(axdir))

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    project = {
        "id": target.name or "axiom-project",
        "version": "0.1.0",
        "domain": domain,
        "platform": platform,
        "lifecycle": "v-model",
        "entry": "greenfield",
        "model_endpoint": model,
        "storage_path": storage,
        "created_at": now,
    }
    (axdir / "project.yaml").write_text(
        __import__("yaml").safe_dump(project, sort_keys=False), encoding="utf-8")

    # engage skills for the domain
    try:
        from packages.skills.engage import engage
        engaged = engage(domain, platform)
    except Exception as exc:
        engaged = {"status": "error", "message": str(exc)}

    # write a README stub
    readme = target / "README.md"
    if not readme.exists():
        readme.write_text(
            f"# {project['id']}\n\nAxiomEmbedded project ({domain} / {platform}).\n\n"
            "Run `axiom doctor` to verify the toolchain.\n", encoding="utf-8")

    return {"status": "ok", "project": str(axdir / "project.yaml"),
            "domain": domain, "platform": platform, "model": model,
            "storage": storage, "engaged_skills": engaged.get("skill_count", 0)
            if isinstance(engaged, dict) else 0}


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="axiom init")
    ap.add_argument("path", nargs="?", default=".")
    ap.add_argument("--domain", default=None)
    ap.add_argument("--platform", default=None)
    ap.add_argument("--model", default=None)
    ap.add_argument("--storage", default=None)
    ap.add_argument("--yes", action="store_true", help="Non-interactive with defaults")
    args = ap.parse_args(argv)
    res = init_project(args.path, args.domain, args.platform, args.model,
                       args.storage, non_interactive=args.yes or not sys.stdin.isatty())
    print(json.dumps(res, indent=2))
    return 0 if res.get("status") == "ok" else 1
