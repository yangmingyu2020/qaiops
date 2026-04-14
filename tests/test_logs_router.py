"""Tests for logs API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_log(client: AsyncClient):
    """POST /api/v1/logs should create a log and return 201."""
    payload = {
        "tool_name": "claude",
        "model_name": "claude-sonnet-4-6",
        "project_id": "test-project",
        "prompt_text": "Explain this code",
        "response_text": "This code does X, Y, Z...",
        "input_tokens": 120,
        "output_tokens": 850,
        "latency_ms": 3200,
        "status_code": 0,
        "tags": ["refactoring"],
    }
    resp = await client.post("/api/v1/logs", json=payload)
    assert resp.status_code == 201

    data = resp.json()
    assert data["tool_name"] == "claude"
    assert data["model_name"] == "claude-sonnet-4-6"
    assert data["input_tokens"] == 120
    assert data["output_tokens"] == 850
    assert data["total_cost"] > 0
    assert data["tags"] == ["refactoring"]
    assert "id" in data


@pytest.mark.asyncio
async def test_create_log_token_estimation(client: AsyncClient):
    """POST /api/v1/logs should estimate tokens when not provided."""
    payload = {
        "tool_name": "gemini",
        "prompt_text": "Hello, world! This is a test prompt.",
        "response_text": "Hello! This is a response.",
    }
    resp = await client.post("/api/v1/logs", json=payload)
    assert resp.status_code == 201

    data = resp.json()
    assert data["input_tokens"] > 0
    assert data["output_tokens"] > 0


@pytest.mark.asyncio
async def test_list_logs_empty(client: AsyncClient):
    """GET /api/v1/logs should return empty list."""
    resp = await client.get("/api/v1/logs")
    assert resp.status_code == 200

    data = resp.json()
    assert data["items"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_list_logs_with_data(client: AsyncClient):
    """GET /api/v1/logs should return logs after creation."""
    # Create a log
    await client.post("/api/v1/logs", json={
        "tool_name": "claude",
        "prompt_text": "test prompt",
    })

    resp = await client.get("/api/v1/logs")
    data = resp.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1


@pytest.mark.asyncio
async def test_list_logs_filter_by_tool(client: AsyncClient):
    """GET /api/v1/logs?tool_name=claude should filter."""
    await client.post("/api/v1/logs", json={"tool_name": "claude", "prompt_text": "a"})
    await client.post("/api/v1/logs", json={"tool_name": "gemini", "prompt_text": "b"})

    resp = await client.get("/api/v1/logs", params={"tool_name": "claude"})
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["tool_name"] == "claude"


@pytest.mark.asyncio
async def test_get_log_by_id(client: AsyncClient):
    """GET /api/v1/logs/{id} should return the log."""
    create_resp = await client.post("/api/v1/logs", json={
        "tool_name": "gpt",
        "prompt_text": "test",
    })
    log_id = create_resp.json()["id"]

    resp = await client.get(f"/api/v1/logs/{log_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == log_id


@pytest.mark.asyncio
async def test_get_log_not_found(client: AsyncClient):
    """GET /api/v1/logs/{id} should return 404 for nonexistent ID."""
    resp = await client.get("/api/v1/logs/nonexistent-id")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """GET /health should return ok."""
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
