"""Doxygen documentation generation wrapper."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def run_doxygen(config: str | Path | None = None, source_dir: str | Path = ".") -> dict:
    exe = shutil.which("doxygen")
    if not exe:
        return {"status": "unavailable", "tool": "doxygen",
                "install_hint": "apt install doxygen / choco install doxygen"}
    cwd = Path(source_dir).resolve()
    if config:
        cmd = [exe, str(Path(config).resolve())]
    else:
        # generate a default config
        subprocess.run([exe, "-g", "Doxyfile"], cwd=str(cwd), capture_output=True)
        cmd = [exe, "Doxyfile"]
    res = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)
    return {"status": "ok" if res.returncode == 0 else "failed",
            "returncode": res.returncode,
            "stdout_tail": (res.stdout or "")[-2000:],
            "stderr_tail": (res.stderr or "")[-2000:]}
