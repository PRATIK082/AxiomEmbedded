# Agent interoperability

AxiomEmbedded supports three distinct concepts:

- **MCP:** expose engineering tools, resources and prompts to an AI client.
- **A2A:** advertise an agent capability and exchange structured tasks with other agents.
- **Provider adapter:** translate model invocation details without embedding provider-specific assumptions in engineering logic.

The engineering contracts live in `schemas/`, `agents/` and `integrations/`; hosted credentials never do.
