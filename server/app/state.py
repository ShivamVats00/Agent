"""AgentState — the typed state that flows through the LangGraph."""

from __future__ import annotations

import operator
from typing import Annotated, Any, Literal
from langgraph.graph import MessagesState


class AgentState(MessagesState):
    """Extends MessagesState with fields for orchestration, tool tracking, and approval."""

    current_node: str
    task: str

    tool_calls_made: Annotated[list[dict[str, Any]], operator.add]
    tool_results: Annotated[list[dict[str, Any]], operator.add]
    errors: Annotated[list[dict[str, Any]], operator.add]

    step_count: int
    max_steps: int

    requires_approval: bool
    approval_status: Literal["pending", "approved", "rejected"] | None
    final_response: str | None
