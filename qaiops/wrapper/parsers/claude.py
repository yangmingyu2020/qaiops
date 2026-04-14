"""Claude CLI output parser."""

import json

from qaiops.wrapper.parsers import ParseResult


def parse(stdout: str, stderr: str) -> ParseResult:
    """Parse Claude CLI output.

    Attempts JSON parsing first (for structured output modes),
    then falls back to plain text capture.
    """
    try:
        data = json.loads(stdout)
        return ParseResult(
            model_name=data.get("model", "claude-sonnet-4-6"),
            response_text=data.get("result", data.get("content", stdout)),
            input_tokens=data.get("usage", {}).get("input_tokens", 0),
            output_tokens=data.get("usage", {}).get("output_tokens", 0),
            raw_response=data,
        )
    except (json.JSONDecodeError, TypeError, ValueError):
        return ParseResult(
            model_name="claude-sonnet-4-6",
            response_text=stdout,
        )
