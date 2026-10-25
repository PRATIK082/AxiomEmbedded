"""Flash/debug probe wrapper: OpenOCD / J-Link invocation (approval-gated)."""
from __future__ import annotations

import subprocess
from pathlib import Path

from packages.toolchain.detect import detect


def flash_openocd(firmware: str, target_cfg: str = "target/stm32f4x.cfg",
                  interface_cfg: str = "interface/stlink.cfg", timeout=120) -> dict:
    if not detect("openocd")["available"]:
        return {"status": "unavailable", "tool": "openocd",
                "install_hint": detect("openocd")["install_hint"]}
    fw = Path(firmware).resolve()
    cmd = ["openocd", "-f", interface_cfg, "-f", target_cfg,
           "-c", f"program {fw} verify reset exit"]
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return {"status": "ok" if res.returncode == 0 else "failed",
            "returncode": res.returncode,
            "stdout_tail": (res.stdout or "")[-2000:],
            "stderr_tail": (res.stderr or "")[-2000:]}


def flash(tool, firmware, **kw):
    tool = (tool or "").lower()
    if tool in ("openocd",):
        return flash_openocd(firmware, kw.get("target_cfg", "target/stm32f4x.cfg"),
                             kw.get("interface_cfg", "interface/stlink.cfg"))
    return {"status": "error", "message": f"unknown flash tool: {tool}"}
