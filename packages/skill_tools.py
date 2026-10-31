# SPDX-License-Identifier: Apache-2.0
"""Deterministic P1 skill wrappers (SDK layer behind MCP + CLI).

Thin, tool-connected generators over the skill framework: they load the
matching axiom-* skill context and emit templated artifacts. Stdlib only,
no network, no shell, no secrets in output. All file writes are confined
to an explicit repo root; every write-capable function defaults to
returning the artifact without writing (dry-run style).
"""

from __future__ import annotations

import csv
import io
import pathlib
import re

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]

SKILL_ID_RE = re.compile(r"^[a-z0-9-]+$")
SECRET_RE = re.compile(r"(?i)(password|passwd|secret|api[_-]?key|token)\s*[:=]")
MAX_FILES_WALK = 20000
MAX_CONFIG_BYTES = 2 * 1024 * 1024
MAX_TRACE_ROWS = 100000

ARTIFACT_TYPES = {
    ".arxml": "ARXML", ".dbc": "DBC", ".dbf": "DBC", ".cdd": "CDD",
    ".odx": "ODX", ".a2l": "A2L", ".c": "C", ".h": "C-header",
    ".cpp": "C++", ".hpp": "C++-header", ".cc": "C++", ".py": "Python",
    ".yaml": "YAML", ".yml": "YAML", ".json": "JSON", ".toml": "TOML",
    ".csv": "trace-data", ".log": "trace-log", ".trc": "trace-log",
    ".asc": "trace-log", ".blf": "trace-log", ".mf4": "trace-data",
    ".md": "documentation", ".cmake": "build", ".txt": "build",
}
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv",
             ".axiom", "target", "build"}


def _err(message: str) -> dict:
    return {"status": "error", "message": message}


def _skill_dir(skill_id: str):
    """Return (skill_dir, None) or (None, error_dict)."""
    if not SKILL_ID_RE.match(skill_id or ""):
        return None, _err(f"invalid skill id: {skill_id!r} "
                          "(allow ^[a-z0-9-]+$)")
    d = (ROOT / "skills" / skill_id).resolve()
    try:
        d.relative_to(ROOT.resolve())
    except ValueError:
        return None, _err(f"skill path escapes skills/: {skill_id!r}")
    if not (d / "SKILL.md").exists():
        return None, _err(f"unknown skill: {skill_id!r}")
    return d, None


def _repo_root(repo_path: str | None):
    base = (ROOT / repo_path) if repo_path else ROOT
    try:
        rp = base.resolve()
    except OSError:
        return None, _err(f"unresolvable repo path: {repo_path!r}")
    if not rp.is_dir():
        return None, _err(f"repo path is not a directory: {repo_path!r}")
    return rp, None


def _output_path(repo: pathlib.Path, output_path: str | None,
                 default_name: str):
    """Resolve a write target confined inside repo. None -> dry-run."""
    if not output_path:
        return None, None
    p = (repo / output_path).resolve() if not pathlib.Path(
        output_path).is_absolute() else pathlib.Path(output_path).resolve()
    try:
        p.relative_to(repo)
    except ValueError:
        return None, _err(f"output path escapes repo: {output_path!r}")
    return p, None


def _write(p: pathlib.Path | None, text: str) -> dict:
    if p is None:
        return {"written": False, "mode": "dry-run"}
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return {"written": True, "mode": "applied", "path": str(p)}


def _frontmatter(skill_dir: pathlib.Path) -> dict:
    body = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    fm = yaml.safe_load(body.split("---\n", 2)[1]) or {}
    return fm, body


def _sections(body: str) -> dict:
    out, cur, buf = {}, None, []
    for line in body.splitlines():
        m = re.match(r"^##\s+(.*)\s*$", line)
        if m:
            if cur is not None:
                out[cur] = "\n".join(buf).strip()
            cur, buf = m.group(1).strip(), []
        elif cur is not None:
            buf.append(line)
    if cur is not None:
        out[cur] = "\n".join(buf).strip()
    return out


def _workflow_steps(body: str) -> list[str]:
    secs = _sections(body)
    text = secs.get("Execution Workflow", "")
    steps = re.findall(r"(?m)^\s*\d+[.)]\s+(.+?)\s*$", text)
    return steps or ["Follow the skill workflow and record evidence."]


def _gates(skill_dir: pathlib.Path) -> list[dict]:
    gates = []
    for f in sorted((skill_dir / "checklists").glob("*.yaml")):
        try:
            data = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        except Exception:
            continue
        for g in data.get("gates", []) or []:
            gates.append({"id": str(g.get("id", "?")),
                          "text": str(g.get("text", "")),
                          "source": f.name})
    return gates


# --------------------------------------------------------------------------
# 1. analyze_repository
# --------------------------------------------------------------------------

def analyze_repository(repo_path: str | None = None) -> dict:
    """Deterministic artifact inventory of a repo (read-only)."""
    repo, err = _repo_root(repo_path)
    if err:
        return err
    by_type: dict[str, dict] = {}
    skipped, total = 0, 0
    for dirpath, dirnames, filenames in _walk(repo):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for fn in sorted(filenames):
            total += 1
            if total > MAX_FILES_WALK:
                skipped += 1
                continue
            p = pathlib.Path(dirpath) / fn
            art = ARTIFACT_TYPES.get(p.suffix.lower(), "other")
            slot = by_type.setdefault(art, {"files": 0, "bytes": 0,
                                            "examples": []})
            try:
                size = p.stat().st_size
            except OSError:
                continue
            slot["files"] += 1
            slot["bytes"] += size
            if len(slot["examples"]) < 3:
                slot["examples"].append(str(p.relative_to(repo)))
    rows = [{"artifact": k, **v} for k, v in sorted(by_type.items())]
    summary = (f"{total} file(s) inventoried across {len(rows)} artifact "
               f"type(s)" + (f" ({skipped} skipped over walk cap)"
                             if skipped else ""))
    return {"status": "ok", "repo": str(repo), "summary": summary,
            "total_files": total, "skipped": skipped,
            "artifacts": rows}


def _walk(repo: pathlib.Path):
    import os

    yield from os.walk(repo)


# --------------------------------------------------------------------------
# 2. generate_checklist
# --------------------------------------------------------------------------

def generate_checklist(skill_id: str, output_path: str | None = None,
                       repo_path: str | None = None) -> dict:
    """Merge a skill's checklists/*.yaml gates into a Markdown checklist."""
    d, err = _skill_dir(skill_id)
    if err:
        return err
    repo, err = _repo_root(repo_path)
    if err:
        return err
    out, err = _output_path(repo, output_path,
                            f"{skill_id}-checklist.md")
    if err:
        return err
    fm, _ = _frontmatter(d)
    gates = _gates(d)
    if not gates:
        return _err(f"skill has no checklist gates: {skill_id!r}")
    lines = [f"# Review Checklist -- {skill_id}",
             f"_Source skill version {fm.get('version', '?')}; "
             f"{len(gates)} gate(s). Human review required for "
             "safety/security gates._", ""]
    for g in gates:
        lines.append(f"- [ ] **{g['id']}** -- {g['text']} `({g['source']})`")
    lines.append("")
    md = "\n".join(lines)
    res = _write(out, md)
    summary = (f"{len(gates)} gate(s) from {skill_id}; "
               + ("written to " + res.get("path", "?")
                  if res["written"] else "dry-run, nothing written"))
    return {"status": "ok", "skill": skill_id, "summary": summary,
            "gates": gates, "markdown": md, **res}


# --------------------------------------------------------------------------
# 3. generate_test_plan
# --------------------------------------------------------------------------

def generate_test_plan(skill_id: str, output_path: str | None = None,
                       repo_path: str | None = None) -> dict:
    """Map a skill's Execution Workflow steps to verification activities."""
    d, err = _skill_dir(skill_id)
    if err:
        return err
    repo, err = _repo_root(repo_path)
    if err:
        return err
    out, err = _output_path(repo, output_path, f"{skill_id}-test-plan.md")
    if err:
        return err
    fm, body = _frontmatter(d)
    steps = _workflow_steps(body)
    lines = [f"# Test Plan -- {skill_id}",
             f"_Derived from Execution Workflow "
             f"(skill version {fm.get('version', '?')})._",
             "", "| ID | Verification activity | Method | Evidence | Status |",
             "|----|-----------------------|--------|----------|--------|"]
    rows = []
    for i, step in enumerate(steps, 1):
        vid = f"VT-{i:02d}"
        rows.append({"id": vid, "activity": step, "method": "TBD",
                     "evidence": "", "status": "Planned"})
        lines.append(f"| {vid} | {step} | TBD |  | Planned |")
    lines.append("")
    lines.append("_Fill Method/Evidence per activity; safety-relevant rows "
                 "need human sign-off._")
    lines.append("")
    md = "\n".join(lines)
    res = _write(out, md)
    return {"status": "ok", "skill": skill_id,
            "summary": f"{len(rows)} verification row(s); "
                       + ("written" if res["written"] else "dry-run"),
            "rows": rows, "markdown": md, **res}


# --------------------------------------------------------------------------
# 4. generate_traceability_matrix
# --------------------------------------------------------------------------

def generate_traceability_matrix(skill_id: str,
                                 output_path: str | None = None,
                                 repo_path: str | None = None) -> dict:
    """Emit Step x Input/Output/Evidence/Status CSV for a skill."""
    from packages.axiom_sdk import skill_manifest

    d, err = _skill_dir(skill_id)
    if err:
        return err
    repo, err = _repo_root(repo_path)
    if err:
        return err
    out, err = _output_path(repo, output_path,
                            f"{skill_id}-traceability.csv")
    if err:
        return err
    _, body = _frontmatter(d)
    steps = _workflow_steps(body)
    man = skill_manifest(skill_id)
    inputs = "; ".join(man.get("inputs", []) or [])
    outputs = "; ".join(man.get("outputs", []) or [])
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["Step", "Activity", "Inputs", "Outputs", "Evidence",
                "Status"])
    for i, step in enumerate(steps, 1):
        w.writerow([f"S-{i:02d}", step, inputs, outputs, "", "Planned"])
    text = buf.getvalue()
    res = _write(out, text)
    return {"status": "ok", "skill": skill_id,
            "summary": f"{len(steps)} trace row(s); "
                       + ("written" if res["written"] else "dry-run"),
            "rows": len(steps), "csv": text, **res}


# --------------------------------------------------------------------------
# 5. generate_report
# --------------------------------------------------------------------------

def generate_report(skill_id: str, run_dir: str | None = None,
                    output_path: str | None = None,
                    repo_path: str | None = None) -> dict:
    """Render a run manifest (or skill context) as Markdown."""
    import json

    d, err = _skill_dir(skill_id)
    if err:
        return err
    repo, err = _repo_root(repo_path)
    if err:
        return err
    out, err = _output_path(repo, output_path, f"{skill_id}-report.md")
    if err:
        return err
    fm, _ = _frontmatter(d)
    gates = _gates(d)
    lines = [f"# Report -- {skill_id}",
             f"_Skill version {fm.get('version', '?')}; "
             f"maturity {((fm.get('axiom') or {}).get('maturity', '?'))}._",
             ""]
    manifest_data = None
    if run_dir:
        mf = ((repo / run_dir) if not pathlib.Path(run_dir).is_absolute()
              else pathlib.Path(run_dir)).resolve()
        try:
            mf.relative_to(repo)
        except ValueError:
            return _err(f"run dir escapes repo: {run_dir!r}")
        if mf.is_dir():
            mf = mf / "run-manifest.json"
        try:
            manifest_data = json.loads(mf.read_text(encoding="utf-8"))
        except OSError:
            return _err(f"run manifest not found: {run_dir!r}")
        except ValueError:
            return _err(f"run manifest is not valid JSON: {run_dir!r}")
        lines += ["## Run summary",
                  f"- timestamp: {manifest_data.get('timestamp', '?')}",
                  f"- inputs: {manifest_data.get('inputs', '?')}",
                  f"- generated files: "
                  f"{len(manifest_data.get('generated_files', []) or [])}",
                  f"- acceptance checks: "
                  f"{manifest_data.get('acceptance_checks', '?')}",
                  f"- warnings: {manifest_data.get('warnings', '?')}", ""]
    lines += ["## Review gates",
              f"{len(gates)} gate(s) defined in "
              f"checklists/ ({', '.join(sorted({g['source'] for g in gates})) or 'none'}).",
              "",
              "_Human review required before release for "
              "safety/security-relevant output._", ""]
    md = "\n".join(lines)
    res = _write(out, md)
    return {"status": "ok", "skill": skill_id,
            "summary": f"report for {skill_id}; "
                       + ("written" if res["written"] else "dry-run"),
            "markdown": md,
            "run_manifest": manifest_data, **res}


# --------------------------------------------------------------------------
# 6. review_configuration
# --------------------------------------------------------------------------

def review_configuration(skill_id: str, config_path: str,
                         repo_path: str | None = None) -> dict:
    """Deterministic structural review of a config file (read-only).

    Checks existence, size cap, YAML/JSON parseability, top-level keys,
    and scans for secret-like assignments (line numbers only -- values
    are never echoed). Findings cross-reference the skill's gate ids.
    """
    d, err = _skill_dir(skill_id)
    if err:
        return err
    repo, err = _repo_root(repo_path)
    if err:
        return err
    if not config_path:
        return _err("config_path is required")
    p = (repo / config_path).resolve()
    try:
        rel = p.relative_to(repo)
    except ValueError:
        return _err(f"config path escapes repo: {config_path!r}")
    if not p.is_file():
        return _err(f"config not found: {config_path!r}")
    try:
        size = p.stat().st_size
    except OSError as exc:
        return _err(f"cannot stat config: {exc}")
    findings: list[dict] = []
    if size > MAX_CONFIG_BYTES:
        findings.append({"severity": "fail", "check": "size",
                         "detail": f"{size} bytes exceeds "
                                   f"{MAX_CONFIG_BYTES} cap"})
        return {"status": "ok", "skill": skill_id,
                "config": str(rel), "verdict": "fail",
                "summary": "config exceeds size cap; not read",
                "findings": findings}
    try:
        text = p.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return _err(f"cannot read config as UTF-8: {exc}")
    if p.suffix.lower() in (".yaml", ".yml"):
        try:
            data = yaml.safe_load(text)
            keys = sorted(data.keys()) if isinstance(data, dict) else []
            findings.append({"severity": "pass", "check": "yaml-parse",
                             "detail": f"valid YAML; top-level keys: {keys}"})
        except yaml.YAMLError as exc:
            findings.append({"severity": "fail", "check": "yaml-parse",
                             "detail": f"invalid YAML: {exc}"})
    elif p.suffix.lower() == ".json":
        import json as _json

        try:
            data = _json.loads(text)
            keys = sorted(data.keys()) if isinstance(data, dict) else []
            findings.append({"severity": "pass", "check": "json-parse",
                             "detail": f"valid JSON; top-level keys: {keys}"})
        except ValueError as exc:
            findings.append({"severity": "fail", "check": "json-parse",
                             "detail": f"invalid JSON: {exc}"})
    else:
        findings.append({"severity": "info", "check": "format",
                         "detail": f"extension {p.suffix or '(none)'}: "
                                   "no structural parser; secret scan only"})
    secret_lines = [i + 1 for i, line in enumerate(text.splitlines())
                    if SECRET_RE.search(line)]
    if secret_lines:
        findings.append({"severity": "fail", "check": "secrets",
                         "detail": f"secret-like assignments at line(s) "
                                   f"{secret_lines}; remove before commit"})
    else:
        findings.append({"severity": "pass", "check": "secrets",
                         "detail": "no secret-like assignments detected"})
    gates = _gates(d)
    verdict = "fail" if any(
        f["severity"] == "fail" for f in findings) else "pass"
    return {"status": "ok", "skill": skill_id, "config": str(rel),
            "verdict": verdict,
            "summary": f"{config_path}: {verdict} "
                       f"({len(findings)} finding(s), {len(gates)} skill "
                       "gate(s) apply)",
            "findings": findings,
            "applicable_gates": [g["id"] for g in gates]}


# --------------------------------------------------------------------------
# 7. analyze_trace
# --------------------------------------------------------------------------

def analyze_trace(trace_path: str,
                  repo_path: str | None = None) -> dict:
    """Deterministic trace summary (read-only, capped rows).

    CSV/TSV: row count, columns, numeric time-range when a time-like
    column exists, value histograms for low-cardinality columns.
    Other text logs: line count plus keyword-hit counts (counts only).
    """
    repo, err = _repo_root(repo_path)
    if err:
        return err
    if not trace_path:
        return _err("trace_path is required")
    p = (repo / trace_path).resolve()
    try:
        rel = p.relative_to(repo)
    except ValueError:
        return _err(f"trace path escapes repo: {trace_path!r}")
    if not p.is_file():
        return _err(f"trace not found: {trace_path!r}")
    suffix = p.suffix.lower()
    if suffix in (".csv", ".tsv"):
        return _analyze_table(p, rel, "\t" if suffix == ".tsv" else ",")
    return _analyze_log(p, rel)


def _analyze_table(p: pathlib.Path, rel: pathlib.Path,
                   delim: str) -> dict:
    try:
        fh = p.open(encoding="utf-8", newline="")
    except OSError as exc:
        return _err(f"cannot read trace: {exc}")
    with fh:
        try:
            reader = csv.DictReader(fh, delimiter=delim)
            cols = list(reader.fieldnames or [])
            rows = 0
            hist: dict[str, dict[str, int]] = {c: {} for c in cols}
            tmin = tmax = None
            time_col = next((c for c in cols
                             if c and c.lower() in ("time", "timestamp",
                                                    "t", "cycle")), None)
            for row in reader:
                rows += 1
                if rows > MAX_TRACE_ROWS:
                    break
                for c in cols:
                    v = (row.get(c) or "")
                    if len(hist[c]) <= 20:
                        hist[c][v] = hist[c].get(v, 0) + 1
                if time_col:
                    try:
                        t = float(row.get(time_col) or "nan")
                        if t == t:  # skip NaN
                            tmin = t if tmin is None else min(tmin, t)
                            tmax = t if tmax is None else max(tmax, t)
                    except ValueError:
                        pass
        except (csv.Error, UnicodeDecodeError) as exc:
            return _err(f"cannot parse trace table: {exc}")
    histograms = {c: h for c, h in sorted(hist.items()) if len(h) <= 20}
    truncated = rows > MAX_TRACE_ROWS
    summary = (f"{rel}: {min(rows, MAX_TRACE_ROWS)} row(s), {len(cols)} "
               f"column(s)" + (", truncated at cap" if truncated else "")
               + (f"; {time_col} range [{tmin}, {tmax}]"
                  if tmin is not None else ""))
    return {"status": "ok", "trace": str(rel), "summary": summary,
            "rows": rows, "truncated": truncated, "columns": cols,
            "time_column": time_col, "time_range": [tmin, tmax]
            if tmin is not None else None, "histograms": histograms}


def _analyze_log(p: pathlib.Path, rel: pathlib.Path) -> dict:
    keywords = ("error", "fail", "timeout", "exception", "dtc", "warn")
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return _err(f"cannot read trace: {exc}")
    lines = text.splitlines()
    if len(lines) > MAX_TRACE_ROWS:
        lines = lines[:MAX_TRACE_ROWS]
    hits = {k: 0 for k in keywords}
    lowered = [ln.lower() for ln in lines]
    for k in keywords:
        hits[k] = sum(1 for ln in lowered if k in ln)
    return {"status": "ok", "trace": str(rel),
            "summary": f"{rel}: {len(lines)} line(s); keyword hits "
                       f"{ {k: v for k, v in hits.items() if v} or 'none'}",
            "lines": len(lines), "keyword_hits": hits}
