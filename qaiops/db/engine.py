"""Database engine and session management."""

import os
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

# DB 파일 경로 (환경변수로 오버라이드 가능)
_db_path = os.environ.get("QAIOPS_DB_PATH", "./db/qaiops.db")
DATABASE_URL = f"sqlite+aiosqlite:///{_db_path}"

engine = create_async_engine(DATABASE_URL, echo=False)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db() -> None:
    """Create all tables if they don't exist."""
    # DB 디렉토리 생성
    db_dir = Path(_db_path).parent
    db_dir.mkdir(parents=True, exist_ok=True)

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session():
    """FastAPI dependency that yields an async DB session."""
    async with async_session() as session:
        yield session
