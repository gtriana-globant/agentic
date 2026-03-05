# Reference JSON Structure

This is the standardized schema that the LangGraph Worker will receive from the MCP tool and persist into Redis.Scenario A: Successful RetrievalWhen the search finds relevant content (e.g., regarding sprint story points ).


```
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
```


Scenario B: Error CaseWhen there is a permission issue (Forbidden), connection failure, or missing configuration.

```
{
  "status": "error",
  "message": "Azure Search Error: Operation returned an invalid status 'Forbidden'",
  "documents": []
}
```

Scenario C: No Results FoundWhen the search executes correctly but no documents match the vector similarity threshold.

```
{
  "status": "success",
  "query_info": {
    "original_query": "Unrelated topic",
    "results_count": 0
  },
  "documents": [],
  "message": "No documents matched the query"
}
```

# Desired Architecture


### 1. Code Restructuring (Modularity & Reusability)

Your current code is monolithic. To reuse components across different MCP servers, you must adopt a standard microservice structure. This is where your new JSON-returning tool shines, as it can be completely decoupled from the server initialization.

**Recommended Directory Structure:**

**Plaintext**

```
mcp-azure-search/
├── core/
│   ├── __init__.py
│   ├── config.py         # Centralized config (Recommended: Pydantic Settings)
│   ├── logger.py         # Structured JSON logging setup
│   └── dependencies.py   # Dependency injection (e.g., Azure Credentials)
├── services/
│   ├── __init__.py
│   └── search_client.py  # Pure Azure Search logic (Decoupled from MCP)
├── tools/
│   ├── __init__.py
│   └── knowledge.py      # Contains your @mcp.tool() returning the structured JSON dict
├── main.py               # Standardized entry point (Initializes FastMCP)
├── requirements.txt      # (Or Pipfile / pyproject.toml)
└── Dockerfile            # Production-optimized Dockerfile
```

**Key Benefit:** If you build an `mcp-fabric` server tomorrow, you can simply copy/paste or package the `core/` folder as an internal private library. This ensures all your MCP servers authenticate and log errors in the exact same standardized way.

---

### 2. Ditching `print()` and `os.getenv()` (Observability & Config)

* **Strict Configuration:** In production, if an environment variable is missing, the pod should crash immediately. Use libraries like `pydantic-settings` to validate variables on startup instead of manual `if not ENDPOINT` checks.
* **Structured Observability:** In AKS, `print()` statements are useless. You must use Python's `logging` library configured to output **JSON logs** . Since your tool now returns a structured JSON object (`status`, `query_info`, `documents`), your logger can easily capture these exact dictionaries. This allows tools like Azure Log Analytics or Datadog to filter by `status: "error"` or correlate traces via a `job_id`.

---

### 3. Extreme Docker Optimization

An AKS container must be **lightweight, secure, and immutable** . Never use the default Python image; use the `slim` version and configure a non-root user.

**Production Dockerfile:**

**Dockerfile**

```
# 1. Lightweight base image
FROM python:3.11-slim as builder

# 2. Python environment variables for production
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# 3. Install necessary system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# 4. Install Python libraries
COPY requirements.txt .
RUN pip install -r requirements.txt

# 5. Create a non-root user for security (Strict requirement in Enterprise AKS)
RUN adduser --disabled-password --gecos "" appuser
USER appuser

# 6. Copy the application code
COPY . .

# 7. Expose the FastMCP default port
EXPOSE 8000

# 8. Startup command
CMD ["python", "main.py"]
```

---

### 4. AKS Security (Credential Management)

* **Workload Identity:** Using `DefaultAzureCredential()` is correct, but in AKS, **you must not use K8s Secrets or Service Principals with passwords in your `.env`** . You need to enable **Azure AD Workload Identity** . This securely binds your Kubernetes Pod's Service Account directly to an Azure Managed Identity.
* **Zero Trust (Networking):** MCP servers **must never be exposed to the public internet** . In AKS, they should be deployed as `ClusterIP` services. Only your "LangGraph Worker" pod should be allowed to communicate with them within the cluster's private Virtual Network (VNet).

---

### 5. Orchestration & Managing Multiple MCPs

If you are running multiple MCP servers (Search, Fabric, SQL), Kubernetes handles the orchestration flawlessly.

* **Independent Microservices:** Each MCP must be a separate Kubernetes *Deployment* .
  * *Advantage:* If the Search MCP crashes due to a traffic spike, it doesn't take down the Fabric MCP.
* **Internal Service Discovery:** Your LangGraph worker doesn't need to know IP addresses. It communicates using Kubernetes internal DNS.
  * Search Endpoint: `http://mcp-search-svc.namespace.svc.cluster.local:8000/sse`
  * Fabric Endpoint: `http://mcp-fabric-svc.namespace.svc.cluster.local:8000/sse`
* **Health Checks (Probes):** Kubernetes needs to know if your server is ready to accept traffic. Ensure your `main.py` exposes a `/health` or `/ping` endpoint so you can configure the `Liveness` and `Readiness` probes in your K8s YAML manifests.

---

### Architectural Flow Summary

1. Your **LangGraph Worker** picks up a job from the Azure Service Bus.
2. The LLM decides it needs documentation and calls the internal URL `http://mcp-search-svc:8000/sse`.
3. The AKS internal networking routes the request to a healthy MCP Pod.
4. The MCP server authenticates using **Workload Identity** (passwordless) and queries Azure AI Search.
5. The MCP returns your **newly structured JSON object** (`status`, `documents`, `metadata.score`) back to the LangGraph worker.
6. **JSON Logs** from both containers stream automatically to Azure Monitor, tied together by the same correlation ID.
