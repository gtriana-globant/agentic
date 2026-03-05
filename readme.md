Reference JSON StructureThis is the standardized schema that the LangGraph Worker will receive from the MCP tool and persist into Redis.Scenario A: Successful RetrievalWhen the search finds relevant content (e.g., regarding sprint story points ).

JSON
{
  "status": "success",
  "query_info": {
    "original_query": "How many story points were completed?",
    "results_count": 1
  },
  "documents": [
    {
      "content": "Sprint 24 focused on implementing... The team committed to 45 story points and successfully delivered 40 points.",
      "metadata": {
        "source": "SPRINT COMPLETION REPORT.pdf",
        "score": 0.8942
      }
    }
  ],
  "message": "Retrieval successful"
}

Scenario B: Error CaseWhen there is a permission issue (Forbidden), connection failure, or missing configuration.

JSON
{
  "status": "error",
  "message": "Azure Search Error: Operation returned an invalid status 'Forbidden'",
  "documents": []
}

Scenario C: No Results FoundWhen the search executes correctly but no documents match the vector similarity threshold.

JSON
{
  "status": "success",
  "query_info": {
    "original_query": "Unrelated topic",
    "results_count": 0
  },
  "documents": [],
  "message": "No documents matched the query"
}
