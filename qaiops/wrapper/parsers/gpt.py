"""GPT / Codex CLI output parser."""

import json

from qaiops.wrapper.parsers import ParseResult


def parse(stdout: str, stderr: str) -> ParseResult:
    """Parse GPT/Codex CLI output.

    Attempts JSON parsing first, then falls back to plain text.
    """
    try:
        data = json.loads(stdout)
        usage = data.get("usage", {})
        return ParseResult(
            model_name=data.get("model", "gpt-4o"),
            response_text=data.get("choices", [{}])[0].get("message", {}).get("content", stdout),
            input_tokens=usage.get("prompt_tokens", 0),
            output_tokens=usage.get("completion_tokens", 0),
            raw_response=data,
        )
    except (json.JSONDecodeError, TypeError, ValueError, IndexError):
        return ParseResult(
            model_name="gpt-4o",
            response_text=stdout,
        )
