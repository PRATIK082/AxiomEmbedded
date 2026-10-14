# Standalone Independence: tool + agent + MCP + PyPI package (ecosystem design)

Status: design (track D). Goal: AxiomEmbedded becomes an independent,
autonomous, standalone product — installed with one command, usable with any
model/host, distributed as a versioned Python package, listed on the MCP
registry, extended via a plugin marketplace, documented on a public docs site.

Non-goal: rebuilding what the OSS ecosystem already does well. Strategy is
**borrow features, own the moat**. The moat is: domain-aware routing
(`configs/domain-routing.yaml`), the skill graph (`skills/catalog.yaml` +
facets + groups), and the evidence/traceability model. Everything else is
interoperability.

## 1. Top open-source building blocks (free to use, verified Oct 2026)

### A. Agent runtimes — interoperate, do NOT rebuild
| Tool | License | Stars/mass | Verdict for us |
|---|---|---|---|
| OpenCode (anomalyco/opencode) | MIT | ~199k, 75+ providers, TUI+desktop+IDE | Primary host: keep `sync_clients.py` mirrors + `axiom oc` launcher first-class |
| Codex CLI (openai/codex) | Apache-2.0 | ~109k, Terminal-Bench top | Support via `.mcp.json` + AGENTS.md (already done); add smoke test |
| Gemini CLI (Google) | Apache-2.0 | ~106k, 1000 free req/day | Same MCP-consumer path; free tier = onboarding funnel |
| Cline | Apache-2.0 | ~63k, VS Code+JetBrains | Marketplace-style install path to copy |
| Aider | Apache-2.0 | ~47k, Python, git-native diff editing | Closest kin: copy its git-commit/diff discipline UX for `axiom run --apply` |
| Goose (Linux Foundation Agentic AI) | Apache-2.0 | ~48k | Recipe-block pattern worth borrowing for skill packs |
| Continue | Apache-2.0 | ~35k, local-model focus | Offline/air-gap story: local models + local tools |
| gptme / RA.Aid / Pi / Crush / Reasonix | MIT/Apache-2.0 | small-large | Watch list; Pi's unified-LLM-API idea informs our provider-neutrality |

### B. MCP layer — align + list
- **Official MCP Python SDK** (`modelcontextprotocol/python-sdk`, MIT) + **spec +
  registry** (`modelcontextprotocol/*`, 90k-star servers repo, 2k+ servers in
  registry, 80k in Glama). Action: migrate `axiom_mcp/server.py` onto the
  official SDK, publish `axiom-embedded` to the MCP registry + awesome lists
  (mcp-finder/awesome-mcp-servers) with install snippet.
- Reference servers to **reuse as tool patterns** (not fork): `mcp-server-git`
  (uvx-runnable), sqlite/filesystem servers. Our `engage/run_plan/context`
  tools stay proprietary-moat; transport becomes stock.

### C. Python packaging — one-command install
- **uv** (Astral, MIT): `uv tool install axiom-embedded` as primary path;
  `hatchling` build backend (already associates well with `pyproject.toml`).
- **pipx** as fallback; **shiv/pex** or PyInstaller for air-gapped single-file
  distribution to defense/aerospace customers.
- Rule: runtime core = stdlib + PyYAML only; every other dep is an extra
  (`eval`, `serve`, `mcp`) so `pip install axiom-embedded` never breaks.

### D. Embedded engineering tools — wrap as `axiom packs`, never reimplement
| Tool | License | Use |
|---|---|---|
| Cppcheck | GPL (safe: subprocess invocation, no linking) | MISRA-adjacent static checks pack |
| Clang-Tidy / LLVM | Apache-2.0 | cert/misra checkers pack |
| gcov/lcov | GPL-invocation-safe | coverage evidence pack |
| Unity + CMock + Ceedling (ThrowTheSwitch) | MIT | host unit-test pack |
| Robot Framework | Apache-2.0 | system-test automation pack |
| Renode (Antmicro) | MIT | SIL simulation pack (no-HW testing story) |
| QEMU / OpenOCD | GPL-invocation-safe | emulation/debug-probe pack |
| Zephyr / FreeRTOS | Apache-2.0/MIT | RTOS reference-profile packs |
| PlatformIO | Apache-2.0 | build-system pack inspiration |

### E. Autonomy infrastructure — adopt patterns
- **Eval harness**: Terminal-Bench methodology (agent+model scored on terminal
  tasks) → our `evaluation/` gets a task set + nightly scoreboard; SWE-bench
  Verified style for fix-defect tasks.
- **Memory**: project-file memory (`axiom.project.yaml`) first; durable
  cross-session memory later (Letta/mem0 pattern, Apache-2.0) — never opaque.
- **Sandbox**: Docker/uvx isolation for `axiom run --apply` (already `oc --isolate`
  pattern); gVisor/bubblewrap for high-assurance sites.
- **Observability**: Langfuse-style (Apache-2.0) run manifests already exist
  (`.axiom/runs`); add trace export.

### F. Docs site — MkDocs Material (MIT)
Versioned docs, search, `mkdocs-click` CLI reference generated from
`axiom --help`, skill catalog pages generated from `registries/skills.json`.
ReadTheDocs or GitHub Pages hosting, free for OSS.

## 2. Independence roadmap (phases)

- **P0 standalone install**: `pyproject.toml` extras split, `uv tool` + `pipx`
  verified in CI, `axiom doctor` as installer self-test.
- **P1 MCP registry**: official-SDK server, registry entry, awesome-list PRs,
  `axiom mcp --check` compat probe against OpenCode/Claude/Codex.
- **P2 toolpacks**: `axiom packs` gains real detectors (cppcheck, clang-tidy,
  renode, ceedling, lcov, robot) with graceful "not installed" guidance.
- **P3 eval + autonomy**: `evaluation/` task set, nightly scoreboard,
  clarification loop already in router; add `--autonomous` bounded mode with
  approval budget.
- **P4 marketplace + docs site**: `registries/` becomes installable index
  (`axiom pack install <skill-group>`), MkDocs site live.

## 3. Decisions needed (user commands next)
1. Primary install vector: `uv tool` vs `pipx` vs both?
2. MCP SDK migration now or after P0?
3. Which toolpack first (recommend: Cppcheck + Unity/Ceedling — highest
   value, lowest license risk)?
4. Docs hosting: GitHub Pages vs ReadTheDocs?
