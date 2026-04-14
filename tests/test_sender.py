"""Tests for async log sender."""

from unittest.mock import patch

from qaiops.wrapper.sender import send_log


def test_send_log_server_unreachable():
    """send_log should not raise even if server is down."""
    payload = {
        "tool_name": "claude",
        "prompt_text": "test",
    }
    # Should not raise any exception
    send_log(payload)


def test_send_log_with_mock_server():
    """send_log should POST to the server."""
    payload = {
        "tool_name": "claude",
        "prompt_text": "test prompt",
    }
    with patch("qaiops.wrapper.sender.httpx.Client") as mock_client:
        mock_instance = mock_client.return_value.__enter__.return_value
        mock_instance.post.return_value.raise_for_status.return_value = None
        send_log(payload)
        mock_instance.post.assert_called_once()
