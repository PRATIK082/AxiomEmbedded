# Ecosystem and interoperability

AxiomEmbedded is designed as a **protocol-neutral engineering backend**. AI clients and agent runtimes can integrate through MCP, A2A, REST, CLI and the Python API without placing provider-specific logic in the core.

## Interoperability layers

| Layer | Purpose |
|---|---|
| CLI | Human and automation entry point |
| Python API | Native automation and integration |
| MCP | Agent-to-tool/resource/prompt interoperability |
| A2A | Agent-to-agent capability/task exchange |
| Git | Source/evidence baseline and collaboration |
| CI | Reproducible verification |

The repository intentionally stores **contracts and adapters**, while client-specific credentials and hosted service state stay outside the repository.
