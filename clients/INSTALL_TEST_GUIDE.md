# AxiomEmbedded — Developer & Tester Guide: Install / Update / Uninstall + MCP map–unmap

Audience: developers (build, install, iterate) and testers (verify every
path, record results). All commands verified on Windows PowerShell,
Python 3.14, `axiom-embedded 0.2.0` (this machine, 2026-10-11).

> Branch note: `install` + MCP mapping exist on **main**. `update`,
> `uninstall`, `--domains`/`--groups` live on branch
> **`skill-frmeworkupdate`** (PR pending). Steps marked **[branch]** need
> `git checkout skill-frmeworkupdate` first.

---

## 1. Prerequisites (developer + tester)

| Need | Check | Fix |
|---|---|---|
| Python ≥ 3.11 | `python --version` | Install from python.org, tick **Add to PATH** |
| pip matches python | `pip --version` (path must match `python`) | Use `python -m pip ...` always — never bare `pip` |
| PyYAML ≥ 6 | auto-installed as the only dependency | `python -m pip install "PyYAML>=6,<7"` |
| Fresh terminal | open **after** Python install | Close/reopen; Scripts dir enters PATH only then |

Golden rule: **always `python -m pip`, never bare `pip`.**
Two Pythons (Store shim + python.org) is the #1 install failure on PC.

## 2. Install the `axiom` exe

### Option A — pip (tester default)

```powershell
cd C:\D\Project\GitHub\AxiomEmbedded
python -m pip install .
where.exe axiom        # expect ...\Python314\Scripts\axiom.exe
axiom --version        # expect 0.2.0
```

### Option B — pipx (developer, isolated)

```powershell
pipx install .
```

### Option C — source checkout (developer, full tree)

```powershell
cd C:\D\Project\GitHub\AxiomEmbedded
python -m axiom_cli --version   # works from repo dir only
```

Expected `pip install .` output: `Successfully built axiom-embedded`
then `Successfully installed axiom-embedded-0.2.0` (wheel ≈ 68 KB).

## 3. Update the exe

```powershell
cd C:\D\Project\GitHub\AxiomEmbedded
git pull
python -m pip install --upgrade --force-reinstall .
axiom --version
```

**[branch]** inside any project: `axiom update --client opencode`
refreshes mapped skill files (use `--force` to overwrite diverged copies).

## 4. Uninstall the exe

```powershell
python -m pip uninstall axiom-embedded   # answers Yes
where.exe axiom                          # expect: not found
```

**[branch]** per-project unmap first (see §6), then uninstall the package.

## 5. Verify install (tester smoke test)

```powershell
axiom --version                 # 0.2.0
axiom doctor --skip-tests       # all lines ok / SKIP
```

| Line | Installed exe | Source checkout |
|---|---|---|
| `axiom_on_path` | path to `axiom.EXE` | `not-found` (normal) |
| `repo` | `SKIP (installed package)` | `PASS` |
| `tests` | `SKIPPED (--skip-tests)` | runs pytest without the flag |

## 6. MCP map / unmap to CLI tools

Mapping = registering the Axiom MCP server **plus** copying skill files so
the CLI agent sees Axiom natively. Unmapping removes both, byte-safe
(diverged user files are kept, never clobbered).

Map (main):

```powershell
axiom install --client opencode --path <project-dir>     # project scope
axiom install --client opencode --global                 # user-global config
```

**[branch]** scoped + lifecycle variants:

```powershell
axiom install --client opencode --domains automotive --path <dir>
axiom install --client claude --groups diagnostics --global
axiom update --client opencode --path <dir>              # refresh mapped files
axiom uninstall --client opencode --path <dir>           # unmap (unmerge + delete pristine copies)
```

Supported `--client` values **[branch: all 10; main: subset]**:
`opencode claude codex gemini copilot cursor cline aider kilo openhands`.

### What mapping writes (verify these)

| Client | MCP registration | Skill files |
|---|---|---|
| opencode | `opencode.json#mcp.axiom-embedded` → `{type:local, command:[python,-m,axiom_cli,mcp], enabled:true}` (or `axiom mcp` when the shim is on PATH) | `.opencode/skills/*/SKILL.md` |
| claude | `.mcp.json` / `~/.claude.json` → `mcpServers.axiom-embedded` | `.claude/skills/`, `.claude/agents/` |
| codex | `.codex/config.toml` → `[mcp_servers.axiom-embedded]` | reads `AGENTS.md`, no copies |
| gemini | `.gemini/settings.json` → `mcpServers.axiom-embedded` | `GEMINI.md` |
| copilot | `.vscode/mcp.json` (see `clients/mcp.json`) | `.github/copilot-instructions.md` |
| cursor / cline / openhands | `.cursor/mcp.json` / `.cline/mcp.json` / `~/.openhands/mcp.json` **[branch]** | mirrors as available |
| aider / kilo | manual snippet (installer prints it; file kept if hand-managed) **[branch]** | — |

## 7. Tester matrix (record Pass/Fail)

| # | Step | Expected |
|---|---|---|
| T1 | `python -m pip install .` | `Successfully installed axiom-embedded-0.2.0` |
| T2 | `axiom --version` | `0.2.0` |
| T3 | `axiom doctor --skip-tests` | all ok/SKIP, zero red |
| T4 | `axiom install --client opencode --path <empty-dir>` | `status: ok`, `written` lists `opencode.json` + `skills/*/SKILL.md` |
| T5 | re-run T4 | `written: []` (idempotent) |
| T6 | open `<dir>/opencode.json` | `mcp.axiom-embedded` entry, `type: local`, `enabled: true` |
| T7 **[branch]** | `axiom update --client opencode --path <dir>` | `status: ok`, stale files refreshed |
| T8 **[branch]** | `axiom uninstall --client opencode --path <dir>` | key unmerged, pristine copies deleted, diverged kept |
| T9 | `python -m pip uninstall axiom-embedded` + `where.exe axiom` | package gone, `axiom` not found |
| T10 | `python -m pytest -q` (source checkout) | green except 2 known pre-existing failures (`dashboard_html` ImportError, research ISO-26262 assertion) |

## 8. Troubleshooting (from real failures on this PC)

1. **`pip install .` fails / wrong place** → `pip` ≠ `python`.
   Check `pip --version` path vs `python --version`. Always `python -m pip install .`
2. **`axiom` not recognized after install** → stale terminal or Scripts
   missing from PATH. Reopen terminal; verify
   `...Python314\Scripts\` is on PATH; `where.exe axiom` must print the exe.
3. **`python -m axiom_cli` → No module named axiom_cli** → wrong
   directory. Either `cd` into the repo or use installed `axiom ...`.
4. **`axiom update/uninstall: invalid choice`** → you're on `main`;
   those commands live on `skill-frmeworkupdate`. `git checkout skill-frmeworkupdate`.
5. **`repo: SKIP`** from `doctor` → normal for pip installs (source-tree
   checks only). Not an error.
