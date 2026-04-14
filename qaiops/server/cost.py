"""Model pricing table and cost calculation."""

import logging

logger = logging.getLogger(__name__)

# 모델별 단가 (USD per 1M tokens)
PRICING: dict[str, dict[str, float]] = {
    # Anthropic
    "claude-opus-4-6": {"input": 15.00, "output": 75.00},
    "claude-sonnet-4-6": {"input": 3.00, "output": 15.00},
    # Google
    "gemini-1.5-pro": {"input": 3.50, "output": 10.50},
    "gemini-2.0-flash": {"input": 0.10, "output": 0.40},
    # OpenAI
    "gpt-4o": {"input": 5.00, "output": 15.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
}


def calculate_cost(model_name: str | None, input_tokens: int, output_tokens: int) -> float:
    """Calculate the USD cost for a given model and token usage.

    Returns 0.0 if the model is unknown.
    """
    if not model_name:
        return 0.0

    pricing = PRICING.get(model_name)
    if pricing is None:
        logger.warning("Unknown model for cost calculation: %s", model_name)
        return 0.0

    cost = (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1_000_000
    return round(cost, 6)
