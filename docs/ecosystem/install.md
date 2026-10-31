# Install (standalone)

Decision (design doc S3.1): **uv primary, pipx fallback**. Both install the
same versioned `axiom-embedded` package; runtime core is stdlib + PyYAML only.

## uv (recommended)

```bash
uv tool install axiom-embedded                # base CLI + MCP server
uv tool install "axiom-embedded[serve]"       # + REST/A2A HTTP transport
uv tool install "axiom-embedded[eval]"        # + evaluation task runner
```

## pipx (fallback)

```bash
pipx install axiom-embedded
pipx install "axiom-embedded[serve]"
```

## Air-gapped / defense sites

```bash
pip download axiom-embedded -d ./wheelhouse   # on a connected machine
pip install --no-index --find-links ./wheelhouse axiom-embedded
```

## Self-test after install

```bash
axiom version
axiom doctor --skip-tests   # installer health: python, deps, repo mode
axiom mcp --check            # MCP handshake + tool-inventory probe
```

`axiom doctor` exits non-zero only on hard requirements (python >= 3.11,
PyYAML, repo presence in checkouts); missing optional tools (cppcheck,
renode, ...) are reported as guidance by `axiom packs`, never as failures.
