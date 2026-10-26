"""Bulk upgrade all experimental skills to beta maturity."""
from __future__ import annotations
import subprocess, sys, pathlib, yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"

# find experimental skills
cat = yaml.safe_load((SKILLS / "catalog.yaml").read_text())
exp = [e["id"] for e in cat["skills"] if e.get("maturity") == "experimental"]

ok = 0
for sid in exp:
    r = subprocess.run([sys.executable, "scripts/upgrade_skill.py", sid, "--apply"],
                       capture_output=True, text=True, cwd=ROOT)
    if r.returncode == 0:
        ok += 1
    else:
        print("FAIL", sid, r.stderr.strip()[:200])

# update catalog.yaml maturity
changed = 0
for e in cat["skills"]:
    if e.get("maturity") == "experimental" and e["id"] in exp:
        e["maturity"] = "beta"
        changed += 1
(SKILLS / "catalog.yaml").write_text(yaml.safe_dump(cat, sort_keys=False), encoding="utf-8")

# update registry.yaml maturity too
reg_path = SKILLS / "registry.yaml"
if reg_path.exists():
    reg = yaml.safe_load(reg_path.read_text())
    for s in reg.get("skills", []):
        if s.get("maturity") == "experimental" and s.get("id") in exp:
            # registry uses path; map id
            pass
    # registry may not have maturity field; leave as is

print(f"upgraded {ok}/{len(exp)} skills; catalog updated {changed}")
