# Quickstart

## Install

```bash
pipx install axiom-embedded   # or: pip install axiom-embedded
axiom doctor
```

## Initialize a project

```bash
mkdir my-fw && cd my-fw
axiom init --yes --domain industrial --platform stm32
axiom doctor
```

## Engage skills

```bash
axiom engage --domain industrial --platform stm32
```

## Build / test / verify

```bash
axiom build --system cmake --source .
axiom test --framework pytest --source .
axiom verify --source .
```

## Research

```bash
axiom research "CAN FD bitrate configuration" --format markdown
```

## Chat

```bash
axiom chat
```

## MCP server (for Claude Code / OpenCode / Cursor)

```bash
axiom mcp --check
# configure your client to run: python -m axiom_cli mcp
```

See `docs/development.md` for cleanup and token-reduction workflow.
