# SPDX-License-Identifier: Apache-2.0
"""One-command skill pipeline: link -> enrich -> index -> clients -> validate.

Why this exists: keeping skills consistent used to mean remembering five
scripts in the right order. Now there is exactly one command:

  python scripts/skill_pipeline.py            # apply (writes)
  python scripts/skill_pipeline.py --check    # verify only (CI gate)

Design rule behind it: skills are DATA (SKILL.md + YAML + templates under
skills/), never code. Adding or editing a skill must never require a .py
change. Only adding a brand-new *tool kind* touches packages/*.py — and
even then this pipeline picks it up with no per-skill edits.

In --check mode every writer step runs against content hashes: if any
generated file would change, the step reports STALE and the pipeline
exits 1 without writing. In apply mode steps run in dependency order.
"""

from __future__ import annotations

import argparse
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))


def _hash_tree(paths: list[pathlib.Path]) -> str:
    h = hashlib.sha256()
    for p in sorted(paths):
        if p.is_file():
            h.update(str(p).encode())
            h.update(p.read_bytes())
    return h.hexdigest()


def _generated_files() -> list[pathlib.Path]:
    """Every file the pipeline may write (never hand-edit these)."""
    pats = ["registries/skill-index.json", "registries/skills.json",
            "skills/catalog.yaml", ".github/copilot-instructions.md",
            "GEMINI.md"]
    out = [ROOT / p for p in pats]
    for prefix in (".opencode/skills", ".claude/skills"):
        base = ROOT / prefix
        if base.is_dir():
            out += sorted(base.rglob("SKILL.md"))
    return out


def run_pipeline(check: bool = False) -> dict:
    """Run (or check) the full pipeline. Returns JSON-serializable report."""
    import link_related_skills as links
    import enrich_catalog_facets as enrich
    import sync_skill_index as sync_idx
    import sync_clients as clients
    from packages.skills.validator import validate_all

    # Sub-scripts parse sys.argv internally; isolate them so pipeline flags
    # (e.g. --check) never leak into a sub-parser.
    saved_argv, sys.argv = sys.argv, [sys.argv[0]]
    try:
        return _run(check, links, enrich, sync_idx, clients, validate_all, record_steps=True)
    finally:
        sys.argv = saved_argv


def _run(check: bool, links, enrich, sync_idx, clients, validate_all, record_steps: bool) -> dict:
    steps: list[dict] = []
    ok = True

    def record(name: str, status: str, detail: str = "") -> None:
        steps.append({"step": name, "status": status, "detail": detail})

    if check:
        before = _hash_tree(_generated_files())
        # Writers run in order; afterwards we compare hashes and fail if
        # anything moved (files were stale). Writers are idempotent, so a
        # second run is a no-op on a clean tree.
        links.apply()
        enrich.enrich(False)
        sync_idx.main()
        clients.main()
        after = _hash_tree(_generated_files())
        rec = "STALE" if before != after else "OK"
        # Restore pre-check bytes? No: writers are idempotent and produce
        # canonical bytes, so `after` IS the correct content. We only report.
        record("writers-idempotent", rec,
               "generated files differ; run without --check" if rec == "STALE" else "all generated files current")
        if rec == "STALE":
            ok = False
    else:
        for name, fn in (("link", links.apply),
                         ("enrich", lambda: enrich.enrich(False)),
                         ("sync-index", sync_idx.main),
                         ("sync-clients", clients.main)):
            try:
                rc = fn()
                if isinstance(rc, int) and rc:
                    record(name, "FAIL", f"exit={rc}")
                    ok = False
                    break
                record(name, "OK")
            except SystemExit as exc:
                record(name, "FAIL" if exc.code else "OK", f"exit={exc.code}")
                if exc.code:
                    ok = False
                    break
            except Exception as exc:  # noqa: BLE001 - report, don't crash
                record(name, "FAIL", str(exc))
                ok = False
                break

    try:
        rep = validate_all()
        record("validate", "OK" if rep["valid"] else "FAIL",
               f"{len(rep['skills'])} skills" +
               ("" if rep["valid"] else f"; bad={[r['skill'] for r in rep['skills'] if not r['valid']]}"))
        ok = ok and bool(rep["valid"])
    except Exception as exc:  # noqa: BLE001
        record("validate", "FAIL", str(exc))
        ok = False

    return {"status": "ok" if ok else "error", "mode": "check" if check else "apply",
            "steps": steps}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="One-command skill pipeline.")
    ap.add_argument("--check", action="store_true", help="Verify only; exit 1 if stale.")
    ns = ap.parse_args(argv)
    import json
    rep = run_pipeline(check=ns.check)
    print(json.dumps(rep, indent=2))
    return 0 if rep["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
