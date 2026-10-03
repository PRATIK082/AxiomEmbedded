# MCP integration

This directory defines the AxiomEmbedded MCP surface.

The intended separation is:

```text
MCP client → AxiomEmbedded MCP server → agent runtime → engineering tools
```

Tool/resource names should be stable, narrowly scoped and schema-backed. Do not expose the entire repository as one giant context resource.
