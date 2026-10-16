# SPDX-License-Identifier: Apache-2.0
"""Fix SKILL.md headers in place (idempotent, text-level, no body changes).

1. Align frontmatter `version:` with manifest.yaml `version:` whenever they
   differ (frontmatter wins in sync-clients, so a stale 0.1.0 there ships
   stale client mirrors).
2. Add a cross-checked `axiom:` metadata block to headers missing one,
   sourced from skills/catalog.yaml (domain/subdomain/category/maturity/
   related_skills/tags/owner) plus the backfilled checklist file that is
   verified to exist. Related skills are filtered to directories on disk.

Only the frontmatter region between the leading `---` markers is touched.
Usage: python scripts/fix_skill_headers.py
"""
from __future__ import annotations

import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
FM_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


def main() -> int:
    cat = yaml.safe_load((ROOT / "skills" / "catalog.yaml").read_text(encoding="utf-8"))
    entries = cat.get("skills", cat if isinstance(cat, list) else [])
    by_id = {e.get("id"): e for e in entries if e.get("id")}
    on_disk = {d.name for d in (ROOT / "skills").iterdir() if d.is_dir()}

    synced, blocked, no_entry = [], [], []
    for d in sorted((ROOT / "skills").iterdir()):
        if not d.is_dir() or d.name.startswith(("_", ".")):
            continue
        md, mp = d / "SKILL.md", d / "manifest.yaml"
        if not (md.exists() and mp.exists()):
            continue
        text = md.read_text(encoding="utf-8")
        m = FM_RE.match(text)
        if not m:
            continue
        fm_text, body = m.group(1), text[m.end():]
        fm = yaml.safe_load(fm_text) or {}
        mf = yaml.safe_load(mp.read_text(encoding="utf-8")) or {}
        changed = False

        want_ver = str(mf.get("version", ""))
        if want_ver and str(fm.get("version", "")) != want_ver:
            fm_text = re.sub(r"^version:\s*\S+\s*$", f"version: {want_ver}",
                             fm_text, count=1, flags=re.MULTILINE)
            synced.append(d.name)
            changed = True

        if "axiom" not in fm:
            entry = by_id.get(d.name)
            if entry is None:
                no_entry.append(d.name)
            else:
                related = [r for r in (entry.get("related_skills") or [])
                           if r in on_disk]
                dotted = str(entry.get("name") or d.name)
                block = {
                    "dotted_name": dotted,
                    "domain": entry.get("domain"),
                    "subdomain": entry.get("subdomain"),
                    "category": entry.get("category"),
                    "maturity": entry.get("maturity", "production"),
                    "owner": entry.get("owner", "axiom-embedded"),
                    "tags": entry.get("tags") or [],
                    "related_skills": related,
                }
                cl = f"checklists/{d.name}-checklist.md"
                if (d / cl).exists():
                    block["checklists"] = [cl]
                rendered = yaml.safe_dump({"axiom": block}, sort_keys=False,
                                          default_flow_style=False).rstrip("\n")
                fm_text = fm_text.rstrip("\n") + "\n" + rendered + "\n"
                blocked.append(d.name)
                changed = True

        if changed:
            # NOTE: fm_text never ends with newline (regex consumes the
            # \n before the closing fence), so re-add it explicitly.
            # Preserve the file's original line endings to avoid diff noise.
            nl = "\r\n" if b"\r\n" in md.read_bytes() else "\n"
            out = "---\n" + fm_text + "\n---\n" + body
            md.write_bytes(out.replace("\n", nl).encode("utf-8"))
    print({"versions_synced": len(synced), "axiom_blocks_added": len(blocked),
           "no_catalog_entry": no_entry, "synced_sample": synced[:5]})
    return 0


if __name__ == "__main__":
    sys.exit(main())
