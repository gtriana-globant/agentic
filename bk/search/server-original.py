import os
from typing import List, Optional
from fastmcp import FastMCP
from dotenv import load_dotenv  # NEW - FOR LOCAL TESTING
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizableTextQuery

load_dotenv() # NEW - TO LOAD ENV_VAR FROM MY LOCAL

# 1. Initialize FastMCP
# This handles the SSE (Server-Sent Events) server automatically
mcp = FastMCP("AzureSearchPoC")

# 2. Configuration (Load from Environment Variables)
ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")  # e.g., https://ai-search-poc-andres.search.windows.net
INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX")   # e.g., rag-poc

if not ENDPOINT:
    raise ValueError("CRITICAL: AZURE_SEARCH_ENDPOINT is not set!")
if not INDEX_NAME:
    raise ValueError("CRITICAL: AZURE_SEARCH_INDEX is not set!")

# 3. Initialize Azure Clients
# We use DefaultAzureCredential to support Workload Identity in AKS automatically
credential = DefaultAzureCredential()

def get_search_client():
    if not ENDPOINT or not INDEX_NAME:
        return None
    
    return SearchClient(
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
        print(f"🔍 Searching in Local: {query}") # NEW - TO SEE A LOG

        client = get_search_client()
        if client is None:
            return "Error: Not environment variables found!"
        
        # Configure the Vector Query
        # This tells Azure: "Take this text, use OpenAI to vectorize it, 
        # and compare it to the 'text_vector' field in the index."
        vector_query = VectorizableTextQuery(
            text=query, 
            k_nearest_neighbors=3, 
            fields="text_vector", # Ensure this matches your index field name
            exhaustive=True
        )
        
        # Execute Search
        results = client.search(
            search_text=None,  # We rely on vector search, not keyword search
            vector_queries=[vector_query],
            select=["chunk", "title"] # Fields to retrieve
        )
        
        # Format Results
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

# Note: FastMCP automatically exposes the server via uvicorn when run