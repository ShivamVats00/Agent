"""Human approval gate — interrupts execution for human review."""

from __future__ import annotations

import logging
from langgraph.types import interrupt
from langchain_core.messages import AIMessage

logger = logging.getLogger(__name__)


async def human_gate_node(state: dict) -> dict:
    """Pause graph execution via interrupt() and wait for external approval.

    Resumes when the /approve endpoint sends Command(resume="approved"|"rejected").
    """
    logger.info("[HumanGate] Requesting human approval...")

    last_ai_msg = None
    for msg in reversed(state["messages"]):
        if isinstance(msg, AIMessage) and msg.content:
            last_ai_msg = msg.content
            break

    approval = interrupt({
        "type": "approval_request",
        "message": "The agent has completed its analysis. Please review and approve.",
        "summary": last_ai_msg[:500] if last_ai_msg else "No summary available.",
    })

    if approval == "approved":
        logger.info("[HumanGate] Approved")
        return {
            "current_node": "human_gate",
            "requires_approval": False,
            "approval_status": "approved",
        }
    else:
        logger.info("[HumanGate] Rejected")
        return {
            "messages": [AIMessage(content="Task rejected by reviewer. Execution halted.")],
            "current_node": "human_gate",
            "requires_approval": False,
            "approval_status": "rejected",
        }
