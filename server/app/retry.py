"""Exponential backoff retry decorator for tool calls."""

from __future__ import annotations

import asyncio
import functools
import logging
from typing import Any, Callable, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


def with_retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 16.0,
    backoff_factor: float = 2.0,
    retryable_exceptions: tuple[type[Exception], ...] = (Exception,),
):
    """Decorator: wraps an async function with exponential backoff retry logic.

    On permanent failure, returns a structured error dict instead of raising,
    so the LLM agent can reason about the failure and try an alternative path.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception: Exception | None = None
            delay = base_delay

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            f"[Retry] {func.__name__} attempt {attempt + 1}/{max_retries + 1} "
                            f"failed: {e}. Retrying in {delay:.1f}s..."
                        )
                        await asyncio.sleep(delay)
                        delay = min(delay * backoff_factor, max_delay)
                    else:
                        logger.error(
                            f"[Retry] {func.__name__} permanently failed after "
                            f"{max_retries + 1} attempts: {e}"
                        )

            return {
                "error": True,
                "tool": func.__name__,
                "message": str(last_exception),
                "attempts": max_retries + 1,
            }

        return wrapper

    return decorator
