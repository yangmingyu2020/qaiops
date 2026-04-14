"""Tests for token counter module."""

from qaiops.server.token_counter import count_tokens


def test_count_tokens_basic():
    count = count_tokens("Hello, world!")
    assert count > 0


def test_count_tokens_empty():
    assert count_tokens("") == 0


def test_count_tokens_with_model():
    count = count_tokens("Hello, world!", "gpt-4o")
    assert count > 0


def test_count_tokens_unknown_model_fallback():
    count = count_tokens("Hello, world!", "unknown-model-xyz")
    assert count > 0


def test_count_tokens_korean():
    count = count_tokens("안녕하세요, 세계!")
    assert count > 0
