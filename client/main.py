# main.py
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from langchain_core.messages import HumanMessage
from agent import app as agent_graph 

# Initialize FastAPI
api = FastAPI(title="Agentic AI API", description="Interface for LangGraph + MCP")

# Define Request and Response schemas
class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str
    context_used: str

@api.post("/ask", response_model=ChatResponse)
async def ask_agent(request: ChatRequest):
    try:
        # Prepare inputs for your existing LangGraph
        inputs = {"messages": [HumanMessage(content=request.query)]}
        
        # Execute the graph
        # We use ainvoke (async invoke) to get the final state
        final_state = await agent_graph.ainvoke(inputs)
        
        # Extract the last message from the LLM and the context from the state
        answer = final_state["messages"][-1].content
        context = final_state.get("context", "No context retrieved")
        
        return ChatResponse(answer=answer, context_used=context)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Run the server on localhost:8080
    #uvicorn.run(api, host="127.0.0.1", port=8080)
    uvicorn.run(api, host="0.0.0.0", port=8080)