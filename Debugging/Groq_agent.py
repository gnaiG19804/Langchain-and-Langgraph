from typing import TypedDict, List
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage, ToolMessage
from langchain_core.tools import tool
import os
from dotenv import load_dotenv

# ===== ENV =====
load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")

# ===== STATE =====
class State(TypedDict):
    messages: List[BaseMessage]

# ===== TOOL =====
@tool
def add(a: float, b: float) -> float:
    """Add two numbers"""
    return a + b

tools = {t.name: t for t in [add]}

# ===== MODEL =====
model = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
).bind_tools(list(tools.values()))

# ===== GRAPH =====
def make_graph():
    workflow = StateGraph(State)

    def agent(state: State):
        response = model.invoke(state["messages"])
        messages = state["messages"] + [response]

        # Handle tool calls
        if response.tool_calls:
            for call in response.tool_calls:
                tool_fn = tools[call["name"]]
                result = tool_fn.invoke(call["args"])
                messages.append(
                    ToolMessage(
                        tool_call_id=call["id"],
                        content=str(result),
                    )
                )

        return {"messages": messages}

    workflow.add_node("agent", agent)
    workflow.add_edge(START, "agent")
    workflow.add_edge("agent", END)

    return workflow.compile()

agent = make_graph()
