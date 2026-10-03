"""Minimal protocol-neutral registration layer; wire to an MCP SDK in deployment."""

class McpRegistry:
    def __init__(self):
        self.tools={}; self.resources={}; self.prompts={}
    def tool(self,name,handler,input_schema=None,output_schema=None):
        self.tools[name]={"handler":handler,"inputSchema":input_schema or {},"outputSchema":output_schema or {}}
    def resource(self,name,provider): self.resources[name]=provider
    def prompt(self,name,template): self.prompts[name]=template
