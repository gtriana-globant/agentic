# Azure Search Logic (deacoupled from mcp)
from typing import List, Dict, Any
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizableTextQuery
from azure.core.exceptions import AzureError

# Import our standardized core components
from core.config import settings
from core.dependencies import get_azure_credential
from core.logger import get_logger

logger = get_logger(__name__)

def get_search_client(index_name: str) -> SearchClient:
    """
    Creates and returns an authenticated Azure SearchClient.
    Uses the centralized configuration and credential manager.
    """
    logger.debug(f"Initializing SearchClient for index: {index_name}")
    return SearchClient(
        endpoint=str(settings.azure_search_endpoint),
        index_name=index_name, #settings.azure_search_index,
        credential=get_azure_credential()
    )

def perform_vector_search(query: str, index_name: str = None, top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Executes a vector search against the Azure AI Search index.
    Returns a clean list of document dictionaries independent of the MCP protocol.
    """
    target_index = index_name or settings.azure_search_index
    try:
        client = get_search_client(target_index)
        logger.info(f"Executing search in '{target_index}' for query: '{query}'")

        # Configure Vector Query using the model specified in the portal
        vector_query = VectorizableTextQuery(
            text=query, 
            k_nearest_neighbors=top_k, 
            fields="text_vector", 
            exhaustive=True
        )
        
        # Execute Search
        results = client.search(
            search_text=None,
            vector_queries=[vector_query],
            select=["chunk", "title"] 
        )
        
        # Extract and format the raw data
        documents = []
        for result in results:
            documents.append({
                "content": result.get("chunk", "No content"),
                "metadata": {
                    "source": result.get("title", "Unknown Source"),
                    "score": result.get("@search.score", 0)
                }
            })
            
        logger.info(f"Search completed successfully. Found {len(documents)} documents.")
        return documents

    except AzureError as e:
        # Catch specific Azure HTTP/Network errors and log them as JSON
        logger.error(f"Azure AI Search encountered an error: {e.message}", exc_info=True)
        raise RuntimeError(f"Search execution failed: {e.message}")
    except Exception as e:
        # Catch any other unexpected Python errors
        logger.error(f"Unexpected error during search: {str(e)}", exc_info=True)
        raise