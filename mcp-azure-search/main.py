# Entry point standardized (Initialize FastMCP)
# server.py
import os
from typing import List, Optional, Dict, Any
from fastmcp import FastMCP
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizableTextQuery

# 1. Load .env only if exists (local dev)
load_dotenv()

# 2. Configuration
ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX")

if not ENDPOINT or not INDEX_NAME:
    raise ValueError("CRITICAL: AZURE_SEARCH_ENDPOINT or INDEX_NAME is not set!")

# 3. Initialize FastMCP
mcp = FastMCP("AzureSearchPoC")

# 4. Initialize Azure Clients
credential = DefaultAzureCredential()
search_client = SearchClient(
    endpoint=ENDPOINT, 
    index_name=INDEX_NAME, 
    credential=credential
)

@mcp.tool()
async def query_knowledge_base(query: str) -> Dict[str, Any]:
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
            select=["chunk", "title"]
        )
        
        # Execute Search
        documents = []
        for result in results:
            documents.append({
                "content": result.get("chunk", "No content"),
                "metadata": {
                    "source": result.get("title", "Unknown Source"),
                    "score": result.get("@search.score", 0)
                }
            })
            
        # Return Data
        return {
            "status": "success",
            "query_info": {
                "original_query": query,
                "results_count": len(documents)
            },
            "documents": documents,
            "message": "Retrieval successful" if documents else "No documents matched the query"
        }

    except Exception as e:
        print(f"❌ Error detected: {str(e)}")
        return {
            "status": "error",
            "message": f"Azure Search Error: {str(e)}",
            "documents": []
        }
    
if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=8000)