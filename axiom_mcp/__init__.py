# SPDX-License-Identifier: Apache-2.0
"""AxiomEmbedded MCP server: every axiom_cli command as a typed stdio tool."""

from axiom_mcp.server import TOOLS, dispatch, serve

__all__ = ["TOOLS", "dispatch", "serve"]
