"""Database models and API schemas."""

import json
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from sqlmodel import Field, SQLModel


# ──────────────────────────────────────────────
# Database Table Models
# ──────────────────────────────────────────────

class QaiOpsLog(SQLModel, table=True):
    """Core log table for AI CLI interactions."""

    __tablename__ = "qaiops_logs"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    tool_name: str = Field(max_length=50, index=True)
    model_name: Optional[str] = Field(default=None, max_length=50)
    project_id: Optional[str] = Field(default=None, max_length=100, index=True)
    directory: Optional[str] = None
    prompt_text: str
    response_text: Optional[str] = None
    input_tokens: int = Field(default=0)
    output_tokens: int = Field(default=0)
    total_cost: float = Field(default=0.0, index=True)
    latency_ms: Optional[int] = None
    status_code: int = Field(default=0)  # 0: 성공, 1: 실패, 2: 타임아웃
    error_message: Optional[str] = None
    tags: Optional[str] = None  # JSON string: ["refactoring", "debug", ...]
    raw_response: Optional[str] = None  # JSON string
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        index=True,
    )


class DailyUsageSummary(SQLModel, table=True):
    """Pre-aggregated daily usage statistics (for future optimization)."""

    __tablename__ = "daily_usage_summary"

    id: Optional[int] = Field(default=None, primary_key=True)
    date: str  # YYYY-MM-DD
    tool_name: str = Field(max_length=50)
    model_name: Optional[str] = Field(default=None, max_length=50)
    total_requests: int = Field(default=0)
    total_tokens: int = Field(default=0)
    total_cost: float = Field(default=0.0)


# ──────────────────────────────────────────────
# API Request / Response Schemas (non-table)
# ──────────────────────────────────────────────

class LogCreateRequest(SQLModel):
    """POST /api/v1/logs request body."""

    tool_name: str
    model_name: Optional[str] = None
    project_id: Optional[str] = None
    directory: Optional[str] = None
    prompt_text: str
    response_text: Optional[str] = None
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: Optional[int] = None
    status_code: int = 0
    error_message: Optional[str] = None
    tags: Optional[list[str]] = None
    raw_response: Optional[dict] = None


class LogResponse(SQLModel):
    """Single log response."""

    id: str
    tool_name: str
    model_name: Optional[str] = None
    project_id: Optional[str] = None
    directory: Optional[str] = None
    prompt_text: str
    response_text: Optional[str] = None
    input_tokens: int = 0
    output_tokens: int = 0
    total_cost: float = 0.0
    latency_ms: Optional[int] = None
    status_code: int = 0
    error_message: Optional[str] = None
    tags: Optional[list[str]] = None
    raw_response: Optional[dict] = None
    created_at: str

    @classmethod
    def from_db(cls, log: QaiOpsLog) -> "LogResponse":
        """Convert a DB row to an API response, deserializing JSON fields."""
        tags = None
        if log.tags:
            try:
                tags = json.loads(log.tags)
            except (json.JSONDecodeError, TypeError):
                tags = None

        raw_response = None
        if log.raw_response:
            try:
                raw_response = json.loads(log.raw_response)
            except (json.JSONDecodeError, TypeError):
                raw_response = None

        return cls(
            id=log.id,
            tool_name=log.tool_name,
            model_name=log.model_name,
            project_id=log.project_id,
            directory=log.directory,
            prompt_text=log.prompt_text,
            response_text=log.response_text,
            input_tokens=log.input_tokens,
            output_tokens=log.output_tokens,
            total_cost=log.total_cost,
            latency_ms=log.latency_ms,
            status_code=log.status_code,
            error_message=log.error_message,
            tags=tags,
            raw_response=raw_response,
            created_at=log.created_at,
        )


class LogListResponse(SQLModel):
    """Paginated log list response."""

    items: list[LogResponse]
    total: int
    page: int
    size: int
    pages: int


class DailyStatsItem(SQLModel):
    """Single day statistics."""

    date: str
    tool_name: str
    total_requests: int
    total_tokens: int
    total_cost: float


class ProjectStatsItem(SQLModel):
    """Project-level statistics."""

    project_id: Optional[str]
    tool_name: str
    request_count: int
    total_tokens: int
    total_cost: float
    avg_latency_ms: Optional[float]
    last_used_at: Optional[str]


class TopCostItem(SQLModel):
    """High-cost request summary."""

    id: str
    tool_name: str
    model_name: Optional[str]
    project_id: Optional[str]
    prompt_text: str
    total_cost: float
    input_tokens: int
    output_tokens: int
    created_at: str
