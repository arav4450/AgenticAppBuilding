"""
calculator_agent.py
Demonstrates an explicit LangGraph workflow using:
- llm.bind_tools(...)
- HumanMessage, AIMessage, ToolMessage, SystemMessage
- StateGraph with custom tool invocation and routing
"""

import os
import sys
import operator
from pathlib import Path
from typing import Annotated, Sequence, TypedDict, Literal
from dotenv import load_dotenv

# Ensure project root is in sys.path
root_dir = str(Path(__file__).resolve().parents[1])
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Load environment variables from root .env
load_dotenv(Path(root_dir) / ".env")

from langchain_core.tools import tool
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    AIMessage,
    ToolMessage,
    SystemMessage,
)
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END


# --------------------------------------------------------------------------
# 1. Tool Definitions
# --------------------------------------------------------------------------
@tool
def add(a: float, b: float) -> float:
    """Add two numbers together."""
    result = a + b
    print(f"[TOOL] add(a={a}, b={b}) -> {result}")
    return result


@tool
def subtract(a: float, b: float) -> float:
    """Subtract the second number (b) from the first number (a)."""
    result = a - b
    print(f"[TOOL] subtract(a={a}, b={b}) -> {result}")
    return result


tools = [add, subtract]
tool_map = {t.name: t for t in tools}

# --------------------------------------------------------------------------
# 2. Bind Tools to LLM
# --------------------------------------------------------------------------
llm = ChatOpenAI(model="gpt-4o", temperature=0.0)
llm_with_tools = llm.bind_tools(tools)


# --------------------------------------------------------------------------
# 3. State & Graph Nodes
# --------------------------------------------------------------------------
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]


def assistant_node(state: AgentState):
    """Invoke the LLM with the message history and return the model's AIMessage."""
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}


def tools_node(state: AgentState):
    """Execute the requested tool calls and produce ToolMessage objects."""
    last_message = state["messages"][-1]
    tool_messages = []

    if isinstance(last_message, AIMessage) and getattr(
        last_message, "tool_calls", None
    ):
        for tc in last_message.tool_calls:
            tool_fn = tool_map[tc["name"]]
            tool_output = tool_fn.invoke(tc["args"])
            tool_messages.append(
                ToolMessage(
                    content=str(tool_output),
                    tool_call_id=tc["id"],
                    name=tc["name"],
                )
            )
    return {"messages": tool_messages}


def should_continue(state: AgentState) -> Literal["tools", END]:
    """Check if the assistant requested tool calls or finished."""
    last_message = state["messages"][-1]
    if isinstance(last_message, AIMessage) and getattr(
        last_message, "tool_calls", None
    ):
        return "tools"
    return END


# --------------------------------------------------------------------------
# 4. Construct LangGraph Workflow
# --------------------------------------------------------------------------
def construct_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("assistant", assistant_node)
    workflow.add_node("tools", tools_node)

    workflow.set_entry_point("assistant")
    workflow.add_conditional_edges(
        "assistant", should_continue, {"tools": "tools", END: END}
    )
    workflow.add_edge("tools", "assistant")

    return workflow.compile()


graph = construct_graph()


# --------------------------------------------------------------------------
# 5. Execution Example
# --------------------------------------------------------------------------
def run_query(user_text: str):
    print(f"\nUser Query: {user_text}")
    print("=" * 60)

    # Initial conversation using SystemMessage and HumanMessage
    initial_messages = [
        SystemMessage(
            content="You are a helpful math assistant. Always use the available tools to compute arithmetic answers."
        ),
        HumanMessage(content=user_text),
    ]

    result = graph.invoke({"messages": initial_messages})

    print("\n--- Message Sequence Breakdown ---")
    for msg in result["messages"]:
        if isinstance(msg, SystemMessage):
            print(f"[SystemMessage] {msg.content}")
        elif isinstance(msg, HumanMessage):
            print(f"[HumanMessage]  {msg.content}")
        elif isinstance(msg, AIMessage):
            if msg.tool_calls:
                for tc in msg.tool_calls:
                    print(f"[AIMessage -> Tool Call] {tc['name']}({tc['args']})")
            else:
                print(f"[AIMessage -> Final Answer] {msg.content}")
        elif isinstance(msg, ToolMessage):
            print(
                f"[ToolMessage] (id={msg.tool_call_id}, name={msg.name}) Result: {msg.content}"
            )

    return result


if __name__ == "__main__":
    query = "What is 125 plus 375, and then subtract 50 from that result?"
    run_query(query)
