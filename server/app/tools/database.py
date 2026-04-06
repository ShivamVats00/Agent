"""Database query tool — executes read-only SQL against a local SQLite database."""

from __future__ import annotations

import aiosqlite
import json
import logging
from pathlib import Path
from langchain_core.tools import tool
from app.config import settings
from app.retry import with_retry

logger = logging.getLogger(__name__)
DB_PATH = settings.db_path


async def _ensure_demo_db() -> None:
    """Create demo tables with sample data if they don't exist."""
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS travel_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT NOT NULL, country TEXT NOT NULL,
                best_month TEXT NOT NULL, avg_temp_celsius REAL,
                avg_rainfall_mm REAL, tourist_rating REAL, notes TEXT
            )
        """)

        cursor = await db.execute("SELECT COUNT(*) FROM travel_data")
        if (await cursor.fetchone())[0] == 0:
            await db.executemany(
                """INSERT INTO travel_data
                   (city, country, best_month, avg_temp_celsius, avg_rainfall_mm, tourist_rating, notes)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                [
                    ("Tokyo", "Japan", "April", 15.4, 125.0, 9.2, "Cherry blossom season"),
                    ("Tokyo", "Japan", "October", 18.2, 197.0, 8.8, "Autumn foliage"),
                    ("Tokyo", "Japan", "March", 10.6, 117.0, 7.5, "End of winter"),
                    ("London", "United Kingdom", "June", 17.8, 45.0, 8.5, "Long daylight hours"),
                    ("London", "United Kingdom", "September", 16.5, 49.0, 8.0, "Post-summer"),
                    ("London", "United Kingdom", "March", 8.9, 37.0, 6.5, "Cool but manageable"),
                    ("New York", "United States", "October", 15.3, 112.0, 9.5, "Fall foliage"),
                    ("New York", "United States", "May", 17.2, 106.0, 8.8, "Spring bloom"),
                    ("New York", "United States", "March", 5.6, 111.0, 6.0, "Cold, fewer tourists"),
                    ("Paris", "France", "June", 19.5, 50.0, 9.0, "Outdoor café season"),
                    ("Paris", "France", "March", 9.5, 48.0, 7.0, "Early spring"),
                    ("Sydney", "Australia", "February", 23.5, 102.0, 8.5, "Late summer"),
                    ("Sydney", "Australia", "March", 22.1, 127.0, 8.0, "Warm autumn"),
                ],
            )

        await db.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL, category TEXT NOT NULL,
                price REAL NOT NULL, stock INTEGER NOT NULL, rating REAL
            )
        """)

        cursor = await db.execute("SELECT COUNT(*) FROM products")
        if (await cursor.fetchone())[0] == 0:
            await db.executemany(
                "INSERT INTO products (name, category, price, stock, rating) VALUES (?, ?, ?, ?, ?)",
                [
                    ("Wireless Headphones", "Electronics", 79.99, 150, 4.5),
                    ("Mechanical Keyboard", "Electronics", 129.99, 85, 4.7),
                    ("Running Shoes", "Sports", 119.99, 200, 4.3),
                    ("Yoga Mat", "Sports", 29.99, 500, 4.6),
                    ("Coffee Maker", "Kitchen", 49.99, 120, 4.2),
                    ("Cast Iron Skillet", "Kitchen", 34.99, 75, 4.8),
                    ("Desk Lamp", "Office", 39.99, 300, 4.1),
                    ("Standing Desk", "Office", 399.99, 40, 4.4),
                ],
            )

        await db.commit()


WRITE_KEYWORDS = {"INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "TRUNCATE"}


@with_retry(max_retries=2, base_delay=0.5)
async def _execute_query(query: str) -> list[dict]:
    """Execute a read-only SQL query."""
    await _ensure_demo_db()

    normalized = query.strip().upper()
    if any(normalized.startswith(kw) for kw in WRITE_KEYWORDS):
        raise ValueError(f"Write operations not allowed: {query[:50]}...")

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(query)
        return [dict(row) for row in await cursor.fetchall()]


@tool
async def query_database(query: str) -> str:
    """Execute a SQL query against the application database.

    Available tables:
    - travel_data (city, country, best_month, avg_temp_celsius, avg_rainfall_mm, tourist_rating, notes)
    - products (name, category, price, stock, rating)

    Only SELECT queries are allowed.

    Args:
        query: A valid SQL SELECT query.
    """
    logger.info(f"[DB] {query}")
    result = await _execute_query(query)

    if isinstance(result, dict) and result.get("error"):
        return json.dumps(result)

    return json.dumps(result, indent=2, default=str)
