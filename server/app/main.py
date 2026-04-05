"""FastAPI application entrypoint."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.routes import router

logging.basicConfig(
    level=logging.INFO if settings.debug else logging.WARNING,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=" * 60)
    logger.info("  🤖 Agentic Workflow Orchestration Framework")
    logger.info("=" * 60)
    logger.info(f"  Model: {settings.gemini_model}")
    logger.info(f"  Debug: {settings.debug}")
    logger.info(f"  API Key: {'✅' if settings.google_api_key else '❌ missing'}")
    logger.info("=" * 60)

    if not settings.google_api_key:
        logger.warning("No GOOGLE_API_KEY set — copy .env.example to .env")

    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="Agentic Workflow Orchestration Framework",
    description="Tool-calling agentic framework powered by LangGraph + Gemini.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
