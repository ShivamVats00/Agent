"""REST and SSE endpoints for the agentic framework."""

from __future__ import annotations

import uuid
import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from langchain_core.messages import HumanMessage
from langgraph.types import Command

from app.graph import get_compiled_graph
from app.api.streaming import stream_graph_events

logger = logging.getLogger(__name__)
router = APIRouter()

_threads: dict[str, dict[str, Any]] = {}


# --- Request / Response models ---

class ChatRequest(BaseModel):
    message: str
    thread_id: str | None = None
    require_approval: bool = False


class ChatResponse(BaseModel):
    thread_id: str
    message: str


class ApprovalRequest(BaseModel):
    decision: str  # "approved" or "rejected"


class ThreadInfo(BaseModel):
    thread_id: str
    status: str
    created_at: str
    message_count: int


# --- Helpers ---

def _build_initial_state(message: str, require_approval: bool = False) -> dict:
    """Build the initial AgentState dict for a new graph invocation."""
    return {
        "messages": [HumanMessage(content=message)],
        "task": message,
        "step_count": 0,
        "max_steps": 10,
        "tool_calls_made": [],
        "tool_results": [],
        "errors": [],
        "requires_approval": require_approval,
        "approval_status": None,
        "current_node": "start",
        "final_response": None,
    }


def _extract_final_message(state: dict) -> str:
    """Pull the last non-tool AI message from the graph state."""
    for msg in reversed(state["messages"]):
        if hasattr(msg, "content") and msg.content and not hasattr(msg, "tool_call_id"):
            return msg.content
    return "Task completed."


# --- Endpoints ---

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Submit a task and run the agent graph to completion."""
    thread_id = request.thread_id or str(uuid.uuid4())
    logger.info(f"[API] Chat — thread={thread_id}")

    compiled = await get_compiled_graph()
    config = {"configurable": {"thread_id": thread_id}}
    input_data = _build_initial_state(request.message, request.require_approval)

    try:
        final_state = await compiled.ainvoke(input_data, config=config)

        _threads[thread_id] = {
            "status": "completed",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "message_count": len(final_state["messages"]),
        }

        return ChatResponse(thread_id=thread_id, message=_extract_final_message(final_state))

    except Exception as e:
        if "interrupt" in str(type(e).__name__).lower() or "GraphInterrupt" in str(type(e)):
            _threads[thread_id] = {
                "status": "awaiting_approval",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "message_count": 0,
            }
            return ChatResponse(
                thread_id=thread_id,
                message="🔒 Agent paused — awaiting human approval via POST /approve/{thread_id}",
            )
        logger.error(f"[API] Chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat/stream/{thread_id}")
async def chat_stream(thread_id: str, message: str):
    """SSE endpoint — streams real-time agent execution events."""
    logger.info(f"[API] Stream — thread={thread_id}")

    compiled = await get_compiled_graph()
    config = {"configurable": {"thread_id": thread_id}}
    input_data = _build_initial_state(message)

    async def event_generator():
        async for event in stream_graph_events(compiled, input_data, config):
            yield {"data": event}

    return EventSourceResponse(event_generator())


@router.post("/approve/{thread_id}")
async def approve(thread_id: str, request: ApprovalRequest):
    """Resume a paused graph after human approval."""
    logger.info(f"[API] Approval — thread={thread_id}, decision={request.decision}")

    compiled = await get_compiled_graph()
    config = {"configurable": {"thread_id": thread_id}}

    try:
        result = await compiled.ainvoke(Command(resume=request.decision), config=config)

        if thread_id in _threads:
            _threads[thread_id]["status"] = f"completed ({request.decision})"

        return {
            "thread_id": thread_id,
            "decision": request.decision,
            "message": _extract_final_message(result),
        }
    except Exception as e:
        logger.error(f"[API] Approval error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/threads")
async def list_threads():
    """List all active threads."""
    return {
        tid: ThreadInfo(thread_id=tid, **info)
        for tid, info in _threads.items()
    }


@router.get("/health")
async def health():
    return {"status": "healthy", "service": "agentic-framework"}
