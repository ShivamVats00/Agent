"""LangGraph assembly — wires nodes into a state machine with conditional edges.

Flow: START → router → (tool_executor → router)* → END
                   └→ human_gate → END
"""

from __future__ import annotations

import logging
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import AIMessage
from app.state import AgentState
from app.nodes.router import router_node
from app.nodes.tool_executor import tool_node
from app.nodes.human_gate import human_gate_node
from app.memory import get_checkpointer

logger = logging.getLogger(__name__)

MAX_STEPS = 10


def should_continue(state: AgentState) -> str:
    """Route after router: tools if tool_calls present, human_gate if max steps, else end."""
    messages = state["messages"]
    last_message = messages[-1]
    step_count = state.get("step_count", 0)

    if step_count >= MAX_STEPS:
        logger.warning(f"[Graph] Max steps ({MAX_STEPS}) reached")
        return "human_gate"

    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tool_executor"

    return "end"


def after_human_gate(state: AgentState) -> str:
    return "end"


def build_graph():
    """Construct the LangGraph StateGraph (uncompiled)."""
    graph = StateGraph(AgentState)

    graph.add_node("router", router_node)
    graph.add_node("tool_executor", tool_node)
    graph.add_node("human_gate", human_gate_node)

    graph.add_edge(START, "router")

    graph.add_conditional_edges(
        "router",
        should_continue,
        {"tool_executor": "tool_executor", "human_gate": "human_gate", "end": END},
    )

    graph.add_edge("tool_executor", "router")

    graph.add_conditional_edges(
        "human_gate",
        after_human_gate,
        {"end": END},
    )

    return graph


async def get_compiled_graph():
    """Compile the graph with SQLite checkpointer for persistence."""
    graph = build_graph()
    checkpointer = await get_checkpointer()

    compiled = graph.compile(
        checkpointer=checkpointer,
        interrupt_before=["human_gate"],
    )

    logger.info("[Graph] Compiled with SQLite checkpointer")
    return compiled
