import os
from typing import List, Optional
from fastmcp import FastMCP
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizableTextQuery

# 1. Load .env only if exists (local dev)
load_dotenv()

# 2. Configuration (Load from Environment Variables)
ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")  # e.g., https://ai-search-poc-andres.search.windows.net
INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX")   # e.g., rag-poc

if not ENDPOINT:
    raise ValueError("CRITICAL: AZURE_SEARCH_ENDPOINT is not set!")
if not INDEX_NAME:
    raise ValueError("CRITICAL: AZURE_SEARCH_INDEX is not set!")

# 3. Initialize FastMCP
mcp = FastMCP("AzureSearchPoC")

# 3. Initialize Azure Clients
credential = DefaultAzureCredential()
search_client = SearchClient(
    endpoint=ENDPOINT, 
    index_name=INDEX_NAME, 
    credential=credential
)

@mcp.tool()
async def query_knowledge_base(query: str) -> str:
    """
    Searches the internal knowledge base (Sprint Reports, Technical Docs) 
    """
    try:
        print(f"🔍 Searching: {query}")

        # Configure Vector Query
        vector_query = VectorizableTextQuery(
            text=query, 
            k_nearest_neighbors=3, 
            fields="text_vector", 
            exhaustive=True
        )
        
        # Execute Search
        results = search_client.search(
            search_text=None,
            vector_queries=[vector_query],
            select=["chunk", "title"] # Fields to retrieve
        )
        
        formatted_response = "Here are the relevant documents found:\n\n"
        count = 0
        for result in results:
            count += 1
            content = result.get("chunk", "No content")
            title = result.get("title", "Unknown Source")
            formatted_response += f"--- Document {count} (Source: {title}) ---\n{content}\n\n"
            
        if count == 0:
            return "No relevant documents found in the knowledge base."
            
        return formatted_response

    except Exception as e:
        print(f"❌ Error detected: {str(e)}")
        return f"Error querying Azure AI Search: {str(e)}"
    
if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=8000)