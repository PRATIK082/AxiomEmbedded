# Development, cleanup, and low-token workflow

## Cleanup record

- Uninstalled the editable `axiom-embedded` package from this PC.
- Removed generated build outputs from the project: `.opencode`, `.claude`, `.claude-plugin`, `build`, `axiom_embedded.egg-info`.
- Removed user-level Axiom state: `~/.axiom`.
- Repository contains only the intended OpenCode v2 compatibility changes:
  - `packages/launcher.py`
  - `tests/test_headless.py`
  - `tests/test_launcher.py`
  - `docs/OPENCODE_COMPAT.md`

Verification after cleanup:

- `python -m compileall -q axiom_cli packages scripts` passed.
- `python -m pytest -q tests/test_launcher.py tests/test_headless.py` passed: 25 passed.

## Token-reduction protocol

1. Compress after each closed phase; keep only decisions, files, commands, and results.
2. Graph-first: use `search_graph`/`trace_path`/`get_code_snippet` before broad file reads.
3. Use targeted reads/grep with `include` and limits; avoid full-repo reads.
4. Run only affected tests during iteration; run the full merge gate once before commit.
5. Avoid repeating full pytest output; use `-q` and targeted test files.
6. Use `axiom doctor --skip-tests` for environment checks.
7. For known environment gates, set `AXIOM_ALLOW_UNTESTED_OPENCODE=1` instead of debugging unrelated failures.

## Install/uninstall/link matrix

- Dev install: `python -m pip install -e ".[test]"` then `python scripts/sync_clients.py`
- Dev remove: `python -m pip uninstall -y axiom-embedded`, then remove `.opencode`, `.claude`, `.claude-plugin`, `build`, `axiom_embedded.egg-info`, and `~/.axiom`
- Standard install: `pip install axiom-embedded`, then `axiom install --client <client> [--global]`
- Standard uninstall: `axiom uninstall --client <client> [--global]`, then `pip uninstall axiom-embedded`
- Full install: standard install plus `python scripts/sync_clients.py`
- Link/unlink coding agents: `axiom install/uninstall --client <opencode|claude|codex|gemini|copilot> [--global]`
