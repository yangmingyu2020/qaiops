"""Tool-specific output parsers."""

from dataclasses import dataclass, field
from typing import Optional, Callable


@dataclass
class ParseResult:
    """Standardized result from parsing a CLI tool's output."""

    model_name: Optional[str] = None
    response_text: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    raw_response: Optional[dict] = None


def get_parser(tool_name: str) -> Callable[[str, str], ParseResult]:
    """Return the appropriate parser function for the given tool."""
    from qaiops.wrapper.parsers import claude, gemini, gpt

    parsers = {
        "claude": claude.parse,
        "gemini": gemini.parse,
        "gpt": gpt.parse,
        "codex": gpt.parse,
    }
    return parsers.get(tool_name, _default_parser)


def _default_parser(stdout: str, stderr: str) -> ParseResult:
    """Fallback parser that captures raw output."""
    return ParseResult(response_text=stdout)
