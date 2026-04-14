"""Statistics endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from qaiops.db.engine import get_session
from qaiops.db.models import (
    AlertItem,
    DailyStatsItem,
    HeatmapItem,
    ProjectStatsItem,
    QaiOpsLog,
    TopCostItem,
)

router = APIRouter()


@router.get("/stats/daily", response_model=list[DailyStatsItem])
async def daily_stats(
    days: int = Query(7, ge=1, le=365),
    tool_name: str | None = None,
    session: AsyncSession = Depends(get_session),
):
    """Get daily usage statistics."""
    query = (
        select(
            func.substr(QaiOpsLog.created_at, 1, 10).label("date"),
            QaiOpsLog.tool_name,
            func.count().label("total_requests"),
            func.sum(QaiOpsLog.input_tokens + QaiOpsLog.output_tokens).label("total_tokens"),
            func.sum(QaiOpsLog.total_cost).label("total_cost"),
        )
        .where(QaiOpsLog.status_code == 0)
        .where(
            QaiOpsLog.created_at >= text(f"datetime('now', '-{days} days')")
        )
        .group_by(func.substr(QaiOpsLog.created_at, 1, 10), QaiOpsLog.tool_name)
        .order_by(func.substr(QaiOpsLog.created_at, 1, 10).desc())
    )

    if tool_name:
        query = query.where(QaiOpsLog.tool_name == tool_name)

    result = await session.execute(query)
    rows = result.all()

    return [
        DailyStatsItem(
            date=row.date,
            tool_name=row.tool_name,
            total_requests=row.total_requests,
            total_tokens=row.total_tokens or 0,
            total_cost=round(row.total_cost or 0, 6),
        )
        for row in rows
    ]


@router.get("/stats/projects", response_model=list[ProjectStatsItem])
async def project_stats(
    session: AsyncSession = Depends(get_session),
):
    """Get project-level usage statistics."""
    query = (
        select(
            QaiOpsLog.project_id,
            QaiOpsLog.tool_name,
            func.count().label("request_count"),
            func.sum(QaiOpsLog.input_tokens + QaiOpsLog.output_tokens).label("total_tokens"),
            func.sum(QaiOpsLog.total_cost).label("total_cost"),
            func.avg(QaiOpsLog.latency_ms).label("avg_latency_ms"),
            func.max(QaiOpsLog.created_at).label("last_used_at"),
        )
        .where(QaiOpsLog.status_code == 0)
        .group_by(QaiOpsLog.project_id, QaiOpsLog.tool_name)
        .order_by(func.sum(QaiOpsLog.total_cost).desc())
    )

    result = await session.execute(query)
    rows = result.all()

    return [
        ProjectStatsItem(
            project_id=row.project_id,
            tool_name=row.tool_name,
            request_count=row.request_count,
            total_tokens=row.total_tokens or 0,
            total_cost=round(row.total_cost or 0, 6),
            avg_latency_ms=round(row.avg_latency_ms, 1) if row.avg_latency_ms else None,
            last_used_at=row.last_used_at,
        )
        for row in rows
    ]


@router.get("/stats/top-costs", response_model=list[TopCostItem])
async def top_costs(
    limit: int = Query(10, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    """Get the most expensive individual requests."""
    query = (
        select(QaiOpsLog)
        .where(QaiOpsLog.status_code == 0)
        .order_by(QaiOpsLog.total_cost.desc())
        .limit(limit)
    )

    result = await session.execute(query)
    logs = result.scalars().all()

    return [
        TopCostItem(
            id=log.id,
            tool_name=log.tool_name,
            model_name=log.model_name,
            project_id=log.project_id,
            prompt_text=log.prompt_text[:200] if log.prompt_text else "",
            total_cost=log.total_cost,
            input_tokens=log.input_tokens,
            output_tokens=log.output_tokens,
            created_at=log.created_at,
        )
        for log in logs
    ]


@router.get("/stats/heatmap", response_model=list[HeatmapItem])
async def heatmap(
    days: int = Query(30, ge=1, le=365),
    session: AsyncSession = Depends(get_session),
):
    """Get heatmap data (date x project) for visualization."""
    query = (
        select(
            func.substr(QaiOpsLog.created_at, 1, 10).label("date"),
            QaiOpsLog.project_id,
            func.sum(QaiOpsLog.input_tokens + QaiOpsLog.output_tokens).label("total_tokens"),
            func.sum(QaiOpsLog.total_cost).label("total_cost"),
            func.count().label("request_count"),
        )
        .where(QaiOpsLog.status_code == 0)
        .where(QaiOpsLog.created_at >= text(f"datetime('now', '-{days} days')"))
        .group_by(func.substr(QaiOpsLog.created_at, 1, 10), QaiOpsLog.project_id)
        .order_by(func.substr(QaiOpsLog.created_at, 1, 10).desc())
    )

    result = await session.execute(query)
    rows = result.all()

    return [
        HeatmapItem(
            date=row.date,
            project_id=row.project_id,
            total_tokens=row.total_tokens or 0,
            total_cost=round(row.total_cost or 0, 6),
            request_count=row.request_count,
        )
        for row in rows
    ]


@router.get("/stats/alerts", response_model=list[AlertItem])
async def alerts(
    threshold: int = Query(10000, ge=0),
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_session),
):
    """Get high-cost alerts (requests exceeding token threshold)."""
    query = (
        select(QaiOpsLog)
        .where(QaiOpsLog.status_code == 0)
        .where((QaiOpsLog.input_tokens + QaiOpsLog.output_tokens) >= threshold)
        .order_by(QaiOpsLog.created_at.desc())
        .limit(limit)
    )

    result = await session.execute(query)
    logs = result.scalars().all()

    return [
        AlertItem(
            id=log.id,
            tool_name=log.tool_name,
            model_name=log.model_name,
            project_id=log.project_id,
            prompt_text=log.prompt_text[:200] if log.prompt_text else "",
            total_tokens=log.input_tokens + log.output_tokens,
            total_cost=log.total_cost,
            created_at=log.created_at,
        )
        for log in logs
    ]
