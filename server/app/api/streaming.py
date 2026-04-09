"""SSE streaming — translates LangGraph events into frontend-consumable JSON."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, AsyncIterator
from langchain_core.messages import AIMessage, ToolMessage

logger = logging.getLogger(__name__)


def format_event(event_type: str, data: dict[str, Any]) -> str:
    return json.dumps({
        "type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": data,
    })


async def stream_graph_events(
    compiled_graph, input_data: dict, config: dict
) -> AsyncIterator[str]:
    """Yield SSE events: node_start, tool_call, tool_result, ai_message, token, complete, error."""
    try:
        yield format_event("stream_start", {"message": "Agent execution started"})

        async for event in compiled_graph.astream_events(
            input_data, config=config, version="v2"
        ):
            kind = event["event"]
            name = event.get("name", "")
            data = event.get("data", {})

            if kind == "on_chain_start" and name in ("router", "tool_executor", "human_gate"):
                yield format_event("node_start", {"node": name, "message": f"Entering {name}"})

            elif kind == "on_chain_end" and name in ("router", "tool_executor", "human_gate"):
                output = data.get("output", {})
                yield format_event("node_end", {"node": name, "step": output.get("step_count")})

            elif kind == "on_chat_model_end":
                output = data.get("output")
                if isinstance(output, AIMessage):
                    if output.tool_calls:
                        for tc in output.tool_calls:
                            yield format_event("tool_call", {
                                "tool": tc["name"], "args": tc["args"], "id": tc["id"],
                            })
                    elif output.content:
                        yield format_event("ai_message", {"content": output.content[:1000], "is_final": True})

            elif kind == "on_tool_end":
                output_data = data.get("output", "")
                if isinstance(output_data, ToolMessage):
                    yield format_event("tool_result", {
                        "tool": output_data.name, "content": output_data.content[:500],
                    })

            elif kind == "on_chat_model_stream":
                chunk = data.get("chunk")
                if chunk and hasattr(chunk, "content") and chunk.content:
                    yield format_event("token", {"content": chunk.content})

        yield format_event("complete", {"message": "Agent execution completed"})

    except Exception as e:
        logger.error(f"[Stream] Error: {e}", exc_info=True)
        yield format_event("error", {"message": str(e), "type": type(e).__name__})
