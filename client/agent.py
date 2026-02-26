import os
import asyncio
from typing import Annotated, TypedDict, List
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from mcp_client import MCPInterface

load_dotenv()

# Define the state of the graph
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], "The messages in the conversation"]
    context: str

# Initialize the Azure LLM
llm = AzureChatOpenAI(
    azure_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)

# Initialize MCP Interface
mcp = MCPInterface()

async def retrieval_node(state: AgentState):
    # Call MCP Tool (text/embedding-3-smoll)
    user_query = state["messages"][-1].content
    print(f"--- RETRIEVING DOCS FOR: {user_query} ---")
    
    # Call the MCP server
    mcp_response = await mcp.fetch_docs(user_query)
    
    # MCP returns a list of document contents
    context_text = "\n".join([doc.text for doc in mcp_response if hasattr(doc, 'text')])
    return {"context": context_text}

async def response_node(state: AgentState):
    # Send context + query to GPT-4 for final formatting.
    system_prompt = SystemMessage(content=(
        "You are an Azure Expert. Use the following retrieved documents "
        f"to answer the user's question.\n\nContext:\n{state['context']}"
    ))
    
    response = await llm.ainvoke([system_prompt] + state["messages"])
    return {"messages": [response]}

# Build the Graph
workflow = StateGraph(AgentState)
workflow.add_node("retriever", retrieval_node)
workflow.add_node("formatter", response_node)
workflow.set_entry_point("retriever")
workflow.add_edge("retriever", "formatter")
workflow.add_edge("formatter", END)

# Expose app to be use by FastAPI
app = workflow.compile()

# Execution block only for Testing
if __name__ == "__main__":
    async def main():
        #inputs = {"messages": [HumanMessage(content="How many story points were committed during sprint 24?")]}
        inputs = {"messages": [HumanMessage(content="How many bugs resolved during sprint 24?")]}
        async for output in app.astream(inputs):
            for key, value in output.items():
                if "messages" in value:
                    print(f"Output from {key}: {value['messages'][-1].content}")
    asyncio.run(main())