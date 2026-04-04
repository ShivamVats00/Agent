"""Calculator tool — safe mathematical expression evaluator."""

from __future__ import annotations

import json
import math
import logging
from langchain_core.tools import tool

logger = logging.getLogger(__name__)

SAFE_MATH = {
    "abs": abs, "round": round, "min": min, "max": max, "sum": sum, "pow": pow,
    "sqrt": math.sqrt, "log": math.log, "log10": math.log10,
    "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "pi": math.pi, "e": math.e, "ceil": math.ceil, "floor": math.floor,
}


@tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression safely.

    Supports: +, -, *, /, **, %, parentheses, and functions
    (sqrt, log, sin, cos, tan, abs, round, min, max, pow, ceil, floor).
    Constants: pi, e.

    Args:
        expression: A math expression (e.g., "sqrt(144) + 2 * pi").
    """
    logger.info(f"[Calc] {expression}")

    try:
        result = eval(expression, {"__builtins__": {}}, SAFE_MATH)
        return json.dumps({"expression": expression, "result": result}, indent=2)
    except Exception as e:
        return json.dumps({"error": True, "expression": expression, "message": str(e)}, indent=2)
