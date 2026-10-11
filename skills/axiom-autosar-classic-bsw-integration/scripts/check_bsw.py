"""BSW integration checker: inventory ARXML-ish config keys, flag gaps. Stdlib only."""
from __future__ import annotations
import pathlib
import sys

EXPECTED = ["RTE", "OS", "COM", "PduR", "CanIf", "CanTp", "Dcm", "Dem", "NvM", "EcuM"]
RTE_KEYS = ["ports", "runnables", "events", "signals"]


def check_config(text: str) -> dict:
    found = {k: (k.lower() in text.lower()) for k in EXPECTED}
    missing = [k for k, v in found.items() if not v]
    findings = []
    for m in missing:
        findings.append({"severity": "major", "element": m,
                         "evidence": "token absent in config text",
                         "action": f"Add {m} configuration or record exclusion rationale"})
    rte_gaps = [k for k in RTE_KEYS if k.lower() not in text.lower()]
    if rte_gaps:
        findings.append({"severity": "minor", "element": "RTE mapping",
                         "evidence": f"absent RTE keys: {rte_gaps}",
                         "action": "Map SWCs to ports/runnables/events/signals"})
    return {"modules_found": [k for k, v in found.items() if v],
            "modules_missing": missing, "findings": findings,
            "verdict": "PASS" if not missing else "REVIEW"}


def main() -> int:
    root = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(".")
    files = list(root.rglob("*.arxml")) + list(root.rglob("*.yaml"))
    if not files:
        print("BSW check: no ARXML/YAML inputs found (PASS with warning: nothing to check)")
        return 0
    worst = 0
    for f in sorted(files)[:50]:
        try:
            res = check_config(f.read_text(encoding="utf-8", errors="replace"))
        except OSError as exc:
            print(f"{f}: unreadable ({exc})")
            worst = max(worst, 1)
            continue
        status = "PASS" if res["verdict"] == "PASS" else "REVIEW"
        print(f"{f}: {status} found={len(res['modules_found'])} "
              f"missing={res['modules_missing']}")
        for fd in res["findings"]:
            print(f"  [{fd['severity']}] {fd['element']}: {fd['action']}")
        if res["verdict"] != "PASS":
            worst = max(worst, 1)
    print("BSW check: " + ("PASS" if worst == 0 else "REVIEW (see findings)"))
    return worst


if __name__ == "__main__":
    raise SystemExit(main())
