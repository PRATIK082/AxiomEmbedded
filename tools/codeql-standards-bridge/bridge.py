"""Local runner for GitHub CodeQL Coding Standards packs (reuse bridge).

Contract (see tools/codeql-standards-bridge/README.md, docs/external-packs.md):
- Query packs stay pristine upstream (MIT; ISO 26262 qualification valid only
  as distributed). This file only shells the CodeQL CLI, parses SARIF 2.1.0,
  and stamps provenance. It contains zero coding-standard queries.
- Fails closed when the CLI is missing, with the download hint.
- Stdlib only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

BRIDGE_ID = "codeql-standards-bridge"
BRIDGE_VERSION = "1.0.0"
MIN_CLI = "2.23.9"
CLI_DOWNLOAD = "https://github.com/github/codeql-cli-binaries/releases"
SARIF_FORMAT = "sarifv2.1.0"

# Short pack key -> upstream pack id (identifiers only, no normative content).
PACKS = {
    "misra-c": "codeql/misra-c-coding-standards",
    "cert-c": "codeql/cert-c-coding-standards",
    "misra-cpp": "codeql/misra-cpp-coding-standards",
    "cert-cpp": "codeql/cert-cpp-coding-standards",
    "autosar-cpp": "codeql/autosar-cpp-coding-standards",
}
SUITES = ("default", "audit", "strict")
LANGUAGES = ("c", "cpp")

_RUN = subprocess.run  # monkeypatched in tests


def check_cli() -> str:
    """Return the CLI version or raise a fail-closed error with install hint."""
    if shutil.which("codeql") is None:
        raise SystemExit(
            f"{BRIDGE_ID}: CodeQL CLI not found. Install CLI >={MIN_CLI} from "
            f"{CLI_DOWNLOAD} and ensure `codeql` is on PATH."
        )
    proc = _RUN(["codeql", "--version"], capture_output=True, text=True)
    line = (proc.stdout or "").strip().splitlines()
    return line[0] if line else "unknown"


def pack_refs(packs: list[str], version: str, suite: str) -> list[str]:
    refs = []
    for key in packs:
        if key not in PACKS:
            raise SystemExit(f"{BRIDGE_ID}: unknown pack '{key}' (choose from {sorted(PACKS)})")
        ref = f"{PACKS[key]}@{version}" if version else PACKS[key]
        if suite != "default":
            ref += f":codeql-suites/{key}-{suite}.qls"
        refs.append(ref)
    return refs


def sarif_to_findings(sarif_path: Path) -> list[dict]:
    try:
        sarif = json.loads(sarif_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        raise SystemExit(f"{BRIDGE_ID}: cannot parse SARIF {sarif_path}: {exc}") from exc
    findings = []
    for run in sarif.get("runs", []):
        for res in run.get("results", []):
            locs = (res.get("locations") or [{}])[0].get("physicalLocation", {})
            art = locs.get("artifactLocation", {})
            region = locs.get("region", {})
            findings.append({
                "rule_id": res.get("ruleId", "unknown"),
                "level": res.get("level", "warning"),
                "message": (res.get("message") or {}).get("text", ""),
                "file": art.get("uri", ""),
                "line": region.get("startLine", 0),
            })
    return sorted(findings, key=lambda f: (f["file"], f["line"], f["rule_id"]))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(source: Path, build: str, db: Path, out: Path, language: str,
        packs: list[str], pack_version: str, suite: str) -> dict:
    if language not in LANGUAGES:
        raise SystemExit(f"{BRIDGE_ID}: language must be one of {LANGUAGES}")
    if suite not in SUITES:
        raise SystemExit(f"{BRIDGE_ID}: suite must be one of {SUITES}")
    cli_version = check_cli()
    refs = pack_refs(packs, pack_version, suite)
    out.mkdir(parents=True, exist_ok=True)

    _RUN(["codeql", "pack", "download", *refs], check=True)
    _RUN(["codeql", "database", "create", "--language", language,
          "--command", build, "--source-root", str(source), str(db)], check=True)
    sarif_path = out / "results.sarif"
    _RUN(["codeql", "database", "analyze", f"--format={SARIF_FORMAT}",
          f"--output={sarif_path}", str(db), *refs], check=True)

    findings = sarif_to_findings(sarif_path)
    (out / "findings.json").write_text(json.dumps(findings, indent=2), encoding="utf-8")
    provenance = {"tool": BRIDGE_ID, "tool_version": BRIDGE_VERSION,
                  "cli_version": cli_version, "packs": refs, "suite": suite,
                  "language": language, "sarif": sarif_path.name,
                  "sarif_sha256": sha(sarif_path),
                  "findings": len(findings)}
    (out / "provenance.json").write_text(json.dumps(provenance, indent=2, sort_keys=True),
                                         encoding="utf-8")
    return provenance


def main() -> int:
    ap = argparse.ArgumentParser(description="Run CodeQL Coding Standards packs locally.")
    ap.add_argument("--source", required=True)
    ap.add_argument("--build", required=True, help="Clean local build command")
    ap.add_argument("--db", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--language", required=True, choices=LANGUAGES)
    ap.add_argument("--pack", dest="packs", action="append", default=[],
                    help=f"Repeatable pack key {sorted(PACKS)}")
    ap.add_argument("--pack-version", default="", help="Pin pack version in CI (e.g. 2.63.0)")
    ap.add_argument("--suite", default="default", choices=SUITES)
    args = ap.parse_args()
    if not args.packs:
        raise SystemExit(f"{BRIDGE_ID}: at least one --pack required (choose from {sorted(PACKS)})")
    info = run(Path(args.source), args.build, Path(args.db), Path(args.out),
               args.language, args.packs, args.pack_version, args.suite)
    print(json.dumps(info, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
