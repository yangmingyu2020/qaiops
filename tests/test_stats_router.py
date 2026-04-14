"""Tests for stats API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_daily_stats_empty(client: AsyncClient):
    """GET /api/v1/stats/daily should return empty list."""
    resp = await client.get("/api/v1/stats/daily")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_daily_stats_with_data(client: AsyncClient):
    """GET /api/v1/stats/daily should aggregate after logs."""
    await client.post("/api/v1/logs", json={
        "tool_name": "claude",
        "model_name": "claude-sonnet-4-6",
        "prompt_text": "test",
        "input_tokens": 100,
        "output_tokens": 200,
    })

    resp = await client.get("/api/v1/stats/daily")
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["tool_name"] == "claude"
    assert data[0]["total_requests"] == 1


@pytest.mark.asyncio
async def test_project_stats_empty(client: AsyncClient):
    """GET /api/v1/stats/projects should return empty list."""
    resp = await client.get("/api/v1/stats/projects")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_project_stats_with_data(client: AsyncClient):
    """GET /api/v1/stats/projects should aggregate by project."""
    await client.post("/api/v1/logs", json={
        "tool_name": "claude",
        "project_id": "my-app",
        "prompt_text": "test",
        "input_tokens": 100,
        "output_tokens": 200,
    })

    resp = await client.get("/api/v1/stats/projects")
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["project_id"] == "my-app"


@pytest.mark.asyncio
async def test_top_costs_empty(client: AsyncClient):
    """GET /api/v1/stats/top-costs should return empty list."""
    resp = await client.get("/api/v1/stats/top-costs")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_top_costs_with_data(client: AsyncClient):
    """GET /api/v1/stats/top-costs should return most expensive requests."""
    await client.post("/api/v1/logs", json={
        "tool_name": "claude",
        "model_name": "claude-opus-4-6",
        "prompt_text": "expensive request",
        "input_tokens": 10000,
        "output_tokens": 5000,
    })

    resp = await client.get("/api/v1/stats/top-costs", params={"limit": 5})
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["total_cost"] > 0
