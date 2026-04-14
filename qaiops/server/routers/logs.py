"""Log CRUD endpoints."""

import json
import math

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from qaiops.db.engine import get_session
from qaiops.db.models import (
    LogCreateRequest,
    LogListResponse,
    LogResponse,
    QaiOpsLog,
)
from qaiops.server.cost import calculate_cost
from qaiops.server.token_counter import count_tokens

router = APIRouter()


@router.post("/logs", response_model=LogResponse, status_code=201)
async def create_log(
    body: LogCreateRequest,
    session: AsyncSession = Depends(get_session),
):
    """Save a new AI interaction log."""
    # 토큰 보정: API 응답에 토큰 수가 없으면 tiktoken으로 추정
    input_tokens = body.input_tokens
    output_tokens = body.output_tokens

    if input_tokens == 0 and body.prompt_text:
        input_tokens = count_tokens(body.prompt_text, body.model_name)
    if output_tokens == 0 and body.response_text:
        output_tokens = count_tokens(body.response_text, body.model_name)

    # 비용 계산
    total_cost = calculate_cost(body.model_name, input_tokens, output_tokens)

    # DB 레코드 생성
    log = QaiOpsLog(
        tool_name=body.tool_name,
        model_name=body.model_name,
        project_id=body.project_id,
        directory=body.directory,
        prompt_text=body.prompt_text,
        response_text=body.response_text,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_cost=total_cost,
        latency_ms=body.latency_ms,
        status_code=body.status_code,
        error_message=body.error_message,
        tags=json.dumps(body.tags) if body.tags else None,
        raw_response=json.dumps(body.raw_response) if body.raw_response else None,
    )

    session.add(log)
    await session.commit()
    await session.refresh(log)

    return LogResponse.from_db(log)


@router.get("/logs", response_model=LogListResponse)
async def list_logs(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    tool_name: str | None = None,
    project_id: str | None = None,
    search: str | None = None,
    session: AsyncSession = Depends(get_session),
):
    """List logs with pagination and filters."""
    # Base query
    query = select(QaiOpsLog)
    count_query = select(func.count()).select_from(QaiOpsLog)

    # Filters
    if tool_name:
        query = query.where(QaiOpsLog.tool_name == tool_name)
        count_query = count_query.where(QaiOpsLog.tool_name == tool_name)
    if project_id:
        query = query.where(QaiOpsLog.project_id == project_id)
        count_query = count_query.where(QaiOpsLog.project_id == project_id)
    if search:
        search_filter = or_(
            QaiOpsLog.prompt_text.contains(search),
            QaiOpsLog.response_text.contains(search),
        )
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)

    # Total count
    total_result = await session.execute(count_query)
    total = total_result.scalar_one()

    # Pagination
    query = query.order_by(QaiOpsLog.created_at.desc())
    query = query.offset((page - 1) * size).limit(size)

    result = await session.execute(query)
    logs = result.scalars().all()

    return LogListResponse(
        items=[LogResponse.from_db(log) for log in logs],
        total=total,
        page=page,
        size=size,
        pages=math.ceil(total / size) if total > 0 else 0,
    )


@router.get("/logs/{log_id}", response_model=LogResponse)
async def get_log(
    log_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Get a single log by ID."""
    result = await session.execute(select(QaiOpsLog).where(QaiOpsLog.id == log_id))
    log = result.scalar_one_or_none()

    if log is None:
        raise HTTPException(status_code=404, detail="Log not found")

    return LogResponse.from_db(log)
