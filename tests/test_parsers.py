"""Tests for CLI output parsers."""

import json

from qaiops.wrapper.parsers import get_parser, ParseResult
from qaiops.wrapper.parsers.claude import parse as claude_parse
from qaiops.wrapper.parsers.gemini import parse as gemini_parse
from qaiops.wrapper.parsers.gpt import parse as gpt_parse


def test_claude_parse_plain_text():
    result = claude_parse("This is a response", "")
    assert result.response_text == "This is a response"
    assert result.model_name == "claude-sonnet-4-6"


def test_claude_parse_json():
    data = {
        "model": "claude-opus-4-6",
        "result": "Parsed content",
        "usage": {"input_tokens": 100, "output_tokens": 200},
    }
    result = claude_parse(json.dumps(data), "")
    assert result.model_name == "claude-opus-4-6"
    assert result.response_text == "Parsed content"
    assert result.input_tokens == 100
    assert result.output_tokens == 200


def test_gemini_parse_plain_text():
    result = gemini_parse("Gemini response", "")
    assert result.response_text == "Gemini response"
    assert result.model_name == "gemini-1.5-pro"


def test_gemini_parse_json():
    data = {
        "model": "gemini-2.0-flash",
        "text": "Gemini structured response",
        "usageMetadata": {"promptTokenCount": 50, "candidatesTokenCount": 150},
    }
    result = gemini_parse(json.dumps(data), "")
    assert result.model_name == "gemini-2.0-flash"
    assert result.input_tokens == 50
    assert result.output_tokens == 150


def test_gpt_parse_plain_text():
    result = gpt_parse("GPT response", "")
    assert result.response_text == "GPT response"
    assert result.model_name == "gpt-4o"


def test_gpt_parse_json():
    data = {
        "model": "gpt-4o",
        "choices": [{"message": {"content": "GPT structured output"}}],
        "usage": {"prompt_tokens": 80, "completion_tokens": 120},
    }
    result = gpt_parse(json.dumps(data), "")
    assert result.response_text == "GPT structured output"
    assert result.input_tokens == 80
    assert result.output_tokens == 120


def test_get_parser_known_tools():
    for tool in ["claude", "gemini", "gpt", "codex"]:
        parser = get_parser(tool)
        assert callable(parser)


def test_get_parser_unknown_tool():
    parser = get_parser("unknown-tool")
    result = parser("some output", "")
    assert isinstance(result, ParseResult)
    assert result.response_text == "some output"
