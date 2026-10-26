# Ghidra integration (D10, deferred)

AxiomEmbedded does **not** bundle Ghidra. For firmware reverse-engineering
tasks, invoke Ghidra headlessly via its own CLI:

```bash
# Headless analysis example
ghidra_headless <project_dir> <project_name> -import <firmware.elf> \
  -postScript ExportFunctions.java -scriptPath ./scripts
```

Axiom provides the surrounding workflow (binary analysis via `axiom binary`,
sigrok capture via `axiom sigrok`, and assurance artifacts) but delegates
disassembly/decompilation to Ghidra or `objdump`/`radare2`.

## Recommended usage
1. Run `axiom binary size <firmware.elf>` and `axiom binary nm <firmware.elf>`
   to triage size/symbols.
2. For deeper RE, run Ghidra headless and feed exported function lists into
   `axiom research --question "..."`.
3. Record findings as a `threat-model` artifact via `axiom threat`.

No automated Ghidra wrapper is shipped; install Ghidra separately.
"""