"""Router node — analyzes the user's task and decides which tools to invoke."""

from __future__ import annotations

import logging
from langchain_core.messages import SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import settings
from app.state import AgentState
from app.tools.database import query_database
from app.tools.weather_api import get_weather
from app.tools.news_api import search_news
from app.tools.calculator import calculate

logger = logging.getLogger(__name__)

ALL_TOOLS = [query_database, get_weather, search_news, calculate]

ROUTER_SYSTEM_PROMPT = """You are an intelligent task router. Your job is to analyze the user's request and use the available tools to gather information needed to complete the task.

You have access to these tools:
1. query_database — Query a SQLite database with SQL. Tables: travel_data, products
2. get_weather — Get current weather for a city
3. search_news — Search for recent news articles on a topic
4. calculate — Evaluate mathematical expressions

Rules:
- Call tools one at a time or in parallel as appropriate.
- If you have enough information to answer, respond with text (no tool call).
- Think step-by-step about what information is needed.
- If a tool call fails, try an alternative approach.
"""


def get_llm():
    """Return the Gemini LLM with all tools bound."""
    llm = ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.google_api_key,
        temperature=0.1,
    )
    return llm.bind_tools(ALL_TOOLS)


async def router_node(state: AgentState) -> dict:
    """Analyze the conversation and generate tool-calling or final-response messages."""
    logger.info(f"[Router] Step {state.get('step_count', 0)}")

    llm = get_llm()
    messages = [SystemMessage(content=ROUTER_SYSTEM_PROMPT)] + state["messages"]
    response = await llm.ainvoke(messages)

    return {
        "messages": [response],
        "current_node": "router",
        "step_count": state.get("step_count", 0) + 1,
    }
