# Entry point standardized (Initialize FastMCP)
import os
from fastmcp import FastMCP
from core.config import settings
from core.logger import get_logger
from tools import register_all_tools

# Initialize structured logging for the main entry point
logger = get_logger(__name__)

def create_app() -> FastMCP:
    """
    Factory function to initialize and configure the FastMCP server.
    """
    logger.info("--- Starting AzureSearchPoC MCP Server ---")
    
    # 1. Initialize FastMCP instance
    # The name here will be visible in the MCP Inspector
    mcp = FastMCP("AzureSearchPoC")
    
    # 2. Register tools from the tools/ directory
    # This maintains the decoupling between the server and the logic
    try:
        register_all_tools(mcp)
        logger.info("All tools registered successfully.")
    except Exception as e:
        logger.critical(f"Failed to register tools: {str(e)}", exc_info=True)
        raise

    return mcp
    
# Create the app instance
mcp = create_app()

if __name__ == "__main__":
    # 3. Run the server with SSE transport
    # Optimized for containerization (Docker/AKS)
    logger.info(f"Server listening on 0.0.0.0:8000 via SSE")
    
    # We use 0.0.0.0 so it can be reached from outside the container in AKS
    mcp.run(
        transport="sse", 
        host="0.0.0.0", 
        port=8000
    )