"""Async log sender — sends logs to the QaiOps server in a background thread."""

import os
import sys
import threading

import httpx

QAIOPS_SERVER_URL = os.environ.get("QAIOPS_SERVER_URL", "http://localhost:8765")
_TIMEOUT = 5.0  # seconds


def send_log(payload: dict) -> None:
    """Send a log payload to the QaiOps server (synchronous).

    All exceptions are caught — the CLI wrapper must never fail due to logging.
    """
    try:
        with httpx.Client(timeout=_TIMEOUT) as client:
            resp = client.post(f"{QAIOPS_SERVER_URL}/api/v1/logs", json=payload)
            resp.raise_for_status()
    except Exception as exc:
        print(f"[qaiops] Warning: could not send log to server: {exc}", file=sys.stderr)


def send_log_async(payload: dict) -> None:
    """Fire-and-forget log sending in a daemon thread."""
    thread = threading.Thread(target=send_log, args=(payload,), daemon=True)
    thread.start()
