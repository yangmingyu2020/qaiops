"""Gemini CLI output parser."""

import json

from qaiops.wrapper.parsers import ParseResult


def parse(stdout: str, stderr: str) -> ParseResult:
    """Parse Gemini CLI output.

    Attempts JSON parsing first, then falls back to plain text.
    """
    try:
        data = json.loads(stdout)
        usage = data.get("usageMetadata", {})
        return ParseResult(
            model_name=data.get("model", "gemini-1.5-pro"),
            response_text=data.get("text", data.get("content", stdout)),
            input_tokens=usage.get("promptTokenCount", 0),
            output_tokens=usage.get("candidatesTokenCount", 0),
            raw_response=data,
        )
    except (json.JSONDecodeError, TypeError, ValueError):
        return ParseResult(
            model_name="gemini-1.5-pro",
            response_text=stdout,
        )
