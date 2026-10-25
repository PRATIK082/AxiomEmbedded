"""Serial/UART log capture wrapper."""
from __future__ import annotations

import subprocess
import time
from pathlib import Path


def capture_serial(port: str, baud: int = 115200, duration_s: int = 5,
                   output: str | None = None) -> dict:
    """Capture serial output for duration_s seconds using pyserial if available,
    else fall back to a subprocess hint. Requires a real device; dry-run safe."""
    try:
        import serial  # type: ignore
    except Exception:
        return {"status": "unavailable", "tool": "pyserial",
                "install_hint": "pip install pyserial"}
    try:
        ser = serial.Serial(port, baud, timeout=1)
        lines = []
        end = time.time() + duration_s
        while time.time() < end:
            raw = ser.readline()
            if raw:
                lines.append(raw.decode("utf-8", errors="replace").rstrip())
        ser.close()
        text = "\n".join(lines)
        if output:
            Path(output).write_text(text, encoding="utf-8")
        return {"status": "ok", "port": port, "baud": baud,
                "lines": len(lines), "output": output, "sample": lines[:20]}
    except Exception as exc:
        return {"status": "error", "port": port, "error": str(exc)}
