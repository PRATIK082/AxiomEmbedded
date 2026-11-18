// SPDX-License-Identifier: Apache-2.0
// Post-install note: the npm wrapper ships only the `axiom` launcher shim.
// The Python backend (skills index, MCP server, validators) comes from the
// PyPI distribution. This hook reports backend status honestly; it never
// fails the install when the backend is absent.
"use strict";

const { spawnSync } = require("node:child_process");

function has(cmd, args) {
  const r = spawnSync(cmd, args, { encoding: "utf-8" });
  return r.status === 0;
}

if (has("axiom", ["--version"]) || has("python", ["-m", "axiom_cli", "--version"])) {
  console.log("[axiom-embedded] backend detected: `axiom` is ready.");
} else {
  console.log(
    "[axiom-embedded] installed the `axiom` launcher. " +
      "Add the Python backend with `pipx install axiom-embedded` " +
      "or run from a source checkout (`python -m axiom_cli ...`)."
  );
}
