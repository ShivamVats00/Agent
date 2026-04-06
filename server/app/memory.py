"""SQLite checkpoint persistence for LangGraph state."""

from __future__ import annotations

import aiosqlite
import logging
from pathlib import Path
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from app.config import settings

logger = logging.getLogger(__name__)

_checkpointer: AsyncSqliteSaver | None = None


async def get_checkpointer() -> AsyncSqliteSaver:
    """Return a singleton AsyncSqliteSaver.

    Uses a raw aiosqlite connection instead of from_conn_string()
    because the latter returns an async context manager, not a BaseCheckpointSaver.
    """
    global _checkpointer

    if _checkpointer is not None:
        return _checkpointer

    db_path = settings.checkpoint_db_path
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"[Memory] Checkpoint DB: {db_path}")

    conn = await aiosqlite.connect(db_path)
    _checkpointer = AsyncSqliteSaver(conn)
    return _checkpointer
