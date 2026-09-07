"""
MCP Integration for FilmFund
"""

import logging
from parallel_api import ParallelGrantSearch

logger = logging.getLogger(__name__)


class MCPServer:
    """MCP server for FilmFund tools."""

    def __init__(self):
        self.tools = {}
        self.parallel_api = ParallelGrantSearch()
        logger.info("MCP Server initialized")

    def register_tool(self, name: str, description: str, handler):
        self.tools[name] = {
            "description": description,
            "handler": handler,
        }

        logger.info(f"Registered tool: {name}")

    def call_tool(self, tool_name: str, *args, **kwargs):
        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}")

        tool = self.tools[tool_name]
        return tool["handler"](*args, **kwargs)

    def list_tools(self) -> list:
        return [
            {
                "name": name,
                "description": tool["description"],
            }
            for name, tool in self.tools.items()
        ]


mcp_server = MCPServer()


def search_parallel_tool(query: str):
    """Search for real film funding opportunities using Parallel."""
    logger.info(f"MCP: Searching '{query}'")
    return mcp_server.parallel_api.search(query)


mcp_server.register_tool(
    "search_parallel",
    "Search for film funding opportunities using Parallel API",
    search_parallel_tool,
)