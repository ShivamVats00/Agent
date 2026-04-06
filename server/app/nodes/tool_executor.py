"""Tool executor node — executes tool calls made by the router."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from langchain_core.messages import ToolMessage
from langgraph.prebuilt import ToolNode
from app.tools.database import query_database
from app.tools.weather_api import get_weather
from app.tools.news_api import search_news
from app.tools.calculator import calculate

logger = logging.getLogger(__name__)

ALL_TOOLS = [query_database, get_weather, search_news, calculate]
tool_executor = ToolNode(ALL_TOOLS)


async def tool_node(state: dict) -> dict:
    """Execute pending tool calls and track results."""
    logger.info("[ToolExecutor] Executing tool calls...")

    result = await tool_executor.ainvoke(state)

    tool_calls_made = []
    for msg in result.get("messages", []):
        if isinstance(msg, ToolMessage):
            tool_calls_made.append({
                "tool": msg.name,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "error" if "error" in msg.content.lower()[:20] else "success",
            })
            logger.info(f"[ToolExecutor] Completed: {msg.name}")

    return {
        "messages": result["messages"],
        "current_node": "tool_executor",
        "tool_calls_made": tool_calls_made,
    }
