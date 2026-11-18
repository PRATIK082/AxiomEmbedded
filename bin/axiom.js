#!/usr/bin/env node
// SPDX-License-Identifier: Apache-2.0
// `axiom` shim: resolves the installed AxiomEmbedded backend.
// 1. `axiom` executable on PATH (pipx / pip install axiom-embedded) wins.
// 2. Fallback: `python -m axiom_cli` from a source checkout.
// 3. Otherwise: honest error with install instructions (never fake success).
"use strict";

const { spawnSync } = require("node:child_process");

function fail(msg) {
  process.stderr.write(`axiom: ${msg}\n`);
  process.exit(1);
}

const args = process.argv.slice(2);

function tryRun(cmd, cmdArgs, opts) {
  const r = spawnSync(cmd, cmdArgs, { stdio: "inherit", ...opts });
  return r.error ? null : r.status;
}

// 1. Prefer a real `axiom` on PATH, but avoid recursing into this shim.
if (process.env.AXIOM_BIN && process.env.AXIOM_BIN !== __filename) {
  const st = tryRun(process.env.AXIOM_BIN, args);
  if (st !== null) process.exit(st);
} else {
  const probe =
    process.platform === "win32"
      ? spawnSync("where", ["axiom"], { encoding: "utf-8" })
      : spawnSync("which", ["axiom"], { encoding: "utf-8" });
  if (probe.status === 0) {
    const bins = String(probe.stdout || "")
      .split(/\r?\n/)
      .map((s) => s.trim())
      .filter(Boolean)
      .filter((p) => p !== __filename);
    for (const b of bins) {
      const st = tryRun(b, args);
      if (st !== null) process.exit(st);
    }
  }
}

// 2. Fallback to python backend.
const py = process.env.AXIOM_PYTHON || "python";
const st = tryRun(py, ["-m", "axiom_cli", ...args]);
if (st !== null) process.exit(st);

// 3. Honest failure.
fail(
  "no AxiomEmbedded backend found. Install it first:\n" +
    "  pipx install axiom-embedded   # recommended\n" +
    "  # or: pip install axiom-embedded\n" +
    "  # or run from a source checkout so `python -m axiom_cli` works."
);
