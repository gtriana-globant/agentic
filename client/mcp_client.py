import os
import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

class MCPInterface:
    def __init__(self):
        self.url = os.getenv(
            "MCP_SERVER_URL", 
            "http://127.0.0.1:8000/sse"
        )
        self.session = None

    async def fetch_docs(self, query: str):
        print(f"--- DEBUG: Connecting to MCP at {self.url} ---")
        try:
            async with sse_client(self.url) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    # Verify tool existence
                    available_tools = await session.list_tools()
                    #print(f"--- DEBUG: Available tools: {[t.name for t in available_tools.tools]} ---")
                    
                    # Call the tool
                    result = await session.call_tool("query_knowledge_base", arguments={"query": query})
                    
                    #print(f"--- DEBUG: Raw MCP Result: {result} ---")
                    return result.content
        except Exception as e:
            print(f"--- DEBUG: MCP Connection Error: {str(e)} ---")
            return []