"""Binary/map/size analyzers (D9): nm, size, objdump, readelf wrappers."""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path


def _run(tool: str, args: list[str], cwd: Path | None = None) -> dict:
    exe = shutil.which(tool)
    if not exe:
        return {"status": "unavailable", "tool": tool,
                "install_hint": f"install {tool} (binutils)"}
    try:
        proc = subprocess.run([exe] + args, capture_output=True, text=True, timeout=120,
                              cwd=str(cwd) if cwd else None)
    except Exception as exc:
        return {"status": "error", "tool": tool, "error": str(exc)}
    return {"status": "ok" if proc.returncode == 0 else "failed",
            "returncode": proc.returncode, "stdout": proc.stdout,
            "stderr": proc.stderr, "tool": tool}


def size_report(elf: str | Path) -> dict:
    res = _run("size", [str(elf)])
    if res["status"] != "ok":
        return res
    # parse 'text data bss dec hex filename'
    lines = res["stdout"].splitlines()
    out = {"raw": res["stdout"]}
    for line in lines:
        parts = line.split()
        if len(parts) >= 4 and parts[0].isdigit():
            out.update({"text": int(parts[0]), "data": int(parts[1]),
                        "bss": int(parts[2]), "total": int(parts[3])})
            break
    return out


def nm_symbols(elf: str | Path, filter_kind: str | None = None) -> dict:
    args = [str(elf)]
    if filter_kind:
        args = ["-C", str(elf)]
    res = _run("nm", args)
    if res["status"] != "ok":
        return res
    syms = []
    for line in res["stdout"].splitlines():
        parts = line.split()
        if len(parts) >= 3:
            syms.append({"addr": parts[0], "type": parts[1], "name": parts[2]})
    if filter_kind:
        syms = [s for s in syms if s["type"] == filter_kind]
    return {"status": "ok", "count": len(syms), "symbols": syms[:200]}


def objdump_sections(elf: str | Path) -> dict:
    """List sections of an ELF via readelf/objdump."""
    import shutil, subprocess
    exe = shutil.which("readelf") or shutil.which("objdump")
    if not exe:
        return {"status": "unavailable", "tool": "readelf/objdump",
                "install_hint": "install binutils"}
    try:
        proc = subprocess.run([exe, "-S", str(elf)], capture_output=True, text=True, timeout=120)
    except Exception as exc:
        return {"status": "error", "error": str(exc)}
    return {"status": "ok" if proc.returncode == 0 else "failed",
            "returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}


def objdump_disassemble(elf: str | Path, function: str | None = None) -> dict:
    args = ["-d", str(elf)]
    if function:
        args = ["-d", f"--disassemble={function}", str(elf)]
    res = _run("objdump", args)
    return res


def map_analyze(map_file: str | Path) -> dict:
    p = Path(map_file)
    if not p.exists():
        return {"status": "error", "error": f"not found: {map_file}"}
    text = p.read_text(encoding="utf-8", errors="ignore")
    # extract section sizes like ".text  0x...  0x..."
    sections = {}
    for line in text.splitlines():
        m = re.match(r"\s*\.(text|data|bss|rodata)\s+0x[0-9a-f]+\s+0x([0-9a-f]+)", line)
        if m:
            sections[m.group(1)] = int(m.group(2), 16)
    return {"status": "ok", "sections": sections, "line_count": len(text.splitlines())}
