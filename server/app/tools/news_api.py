"""News search tool — searches for recent news articles."""

from __future__ import annotations

import httpx
import json
import logging
from langchain_core.tools import tool
from app.config import settings
from app.retry import with_retry

logger = logging.getLogger(__name__)

MOCK_NEWS = {
    "technology": [
        {"title": "AI Agents Reshape Enterprise Software Landscape", "source": "TechCrunch", "summary": "Major tech companies rapidly adopt agentic AI frameworks, reducing manual intervention by 60%."},
        {"title": "Open-Source LLM Frameworks See 300% Growth", "source": "The Verge", "summary": "LangGraph and similar tools dominate GitHub trending charts."},
        {"title": "New Security Standards for AI Tool-Calling Systems", "source": "Wired", "summary": "Industry proposes sandboxing and guardrail requirements for AI tool-calling."},
    ],
    "travel": [
        {"title": "Japan Sees Record Tourism in Spring 2026", "source": "Travel Weekly", "summary": "March-April bookings up 45% year-over-year."},
        {"title": "London Named Top City Break for 2026", "source": "Lonely Planet", "summary": "New exhibitions push London to top of wish lists."},
        {"title": "Budget Airlines Launch New Asian Routes", "source": "Bloomberg", "summary": "Trans-Pacific pricing makes Tokyo and Sydney more accessible."},
    ],
    "finance": [
        {"title": "Global Markets Rally on Tech Earnings", "source": "Reuters", "summary": "S&P 500 hits highs driven by AI stock surge."},
        {"title": "Crypto Regulation Framework Takes Shape", "source": "Financial Times", "summary": "Major economies agree on coordinated regulatory approach."},
    ],
    "default": [
        {"title": "Major Scientific Breakthrough Announced", "source": "Nature", "summary": "Landmark findings reshape understanding of complex systems."},
        {"title": "Global Climate Summit Reaches Agreement", "source": "BBC", "summary": "195 nations commit to accelerated emission reduction."},
    ],
}

KEYWORD_MAP = {
    "technology": ["tech", "ai", "software", "coding"],
    "travel": ["travel", "tourism", "flight", "hotel"],
    "finance": ["finance", "market", "stock", "crypto"],
}


@with_retry(max_retries=3, base_delay=1.0)
async def _search_news(query: str) -> list[dict]:
    """Search NewsAPI or return category-matched mock data."""
    api_key = settings.news_api_key

    if not api_key:
        query_lower = query.lower()

        for category, articles in MOCK_NEWS.items():
            if category != "default" and category in query_lower:
                return articles

        for category, keywords in KEYWORD_MAP.items():
            if any(kw in query_lower for kw in keywords):
                return MOCK_NEWS[category]

        return MOCK_NEWS["default"]

    url = "https://newsapi.org/v2/everything"
    params = {"q": query, "apiKey": api_key, "pageSize": 5, "sortBy": "relevancy"}

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

    return [
        {"title": a["title"], "source": a["source"]["name"], "summary": a.get("description", "")}
        for a in data.get("articles", [])[:5]
    ]


@tool
async def search_news(query: str) -> str:
    """Search for recent news articles related to a topic.

    Args:
        query: Search query (e.g., "AI technology trends", "Tokyo travel").
    """
    logger.info(f"[News] {query}")
    result = await _search_news(query)

    if isinstance(result, dict) and result.get("error"):
        return json.dumps(result)

    return json.dumps(result, indent=2)
