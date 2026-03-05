from fastmcp import FastMCP
from .knowledge import query_knowledge_base

def register_all_tools(mcp: FastMCP) -> None:
    """
    Registers all available tools with the main FastMCP server instance.
    This keeps tool definitions decoupled from the server initialization.
    """
    # Register the knowledge base search tool
    mcp.add_tool(query_knowledge_base)
    
    # Example for future sprints:
    # mcp.add_tool(query_fabric_lakehouse)
    # mcp.add_tool(get_service_bus_status)