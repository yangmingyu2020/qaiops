"""Tests for cost calculation module."""

from qaiops.server.cost import calculate_cost


def test_claude_opus_cost():
    cost = calculate_cost("claude-opus-4-6", 1000, 1000)
    expected = (1000 * 15.00 + 1000 * 75.00) / 1_000_000
    assert cost == round(expected, 6)


def test_claude_sonnet_cost():
    cost = calculate_cost("claude-sonnet-4-6", 1000, 1000)
    expected = (1000 * 3.00 + 1000 * 15.00) / 1_000_000
    assert cost == round(expected, 6)


def test_gemini_cost():
    cost = calculate_cost("gemini-1.5-pro", 1000, 1000)
    expected = (1000 * 3.50 + 1000 * 10.50) / 1_000_000
    assert cost == round(expected, 6)


def test_gpt4o_cost():
    cost = calculate_cost("gpt-4o", 1000, 1000)
    expected = (1000 * 5.00 + 1000 * 15.00) / 1_000_000
    assert cost == round(expected, 6)


def test_unknown_model_returns_zero():
    assert calculate_cost("unknown-model", 1000, 1000) == 0.0


def test_none_model_returns_zero():
    assert calculate_cost(None, 1000, 1000) == 0.0


def test_zero_tokens():
    assert calculate_cost("gpt-4o", 0, 0) == 0.0
