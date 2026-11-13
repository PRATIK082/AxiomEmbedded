"""Rebuild skills/registry.yaml from skills/catalog.yaml (idempotent)."""
from __future__ import annotations
import pathlib, yaml

ROOT = pathlib.Path(r"E:\My_Project\My_Github\AxiomEmbedded")
cat = yaml.safe_load((ROOT / "skills" / "catalog.yaml").read_text(encoding="utf-8"))
entries = []
for e in cat["skills"]:
    sid = e["id"]
    domain = e.get("domain", "all")
    maturity = e.get("maturity", "experimental")
    if sid.startswith("axiom-"):
        name = "axiom." + domain + "." + sid[len("axiom-"):].replace("-", ".")
    else:
        name = "axiom.legacy." + sid
    entries.append({"name": name, "path": f"skills/{sid}", "domain": domain, "maturity": maturity})
reg = {"version": 1, "skills": entries}
(ROOT / "skills" / "registry.yaml").write_text(
    yaml.safe_dump(reg, sort_keys=False, allow_unicode=False), encoding="utf-8")
print("wrote", len(entries), "entries")