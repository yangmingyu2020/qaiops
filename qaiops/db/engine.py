"""Database engine and session management."""

import os
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from sqlmodel import SQLModel

# DB 파일 경로 (환경변수로 오버라이드 가능)
_db_path = os.environ.get("QAIOPS_DB_PATH", "./db/qaiops.db")
DATABASE_URL = f"sqlite+aiosqlite:///{_db_path}"

engine = create_async_engine(DATABASE_URL, echo=False)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db() -> None:
    """Create all tables and FTS5 index if they don't exist."""
    db_dir = Path(_db_path).parent
    db_dir.mkdir(parents=True, exist_ok=True)

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

        # FTS5 virtual table for full-text search
        await conn.execute(
            text("""
                CREATE VIRTUAL TABLE IF NOT EXISTS qaiops_logs_fts
                USING fts5(prompt_text, response_text, content=qaiops_logs, content_rowid=rowid)
            """)
        )

        # Triggers to keep FTS index in sync
        for trigger_sql in [
            """
            CREATE TRIGGER IF NOT EXISTS qaiops_logs_ai AFTER INSERT ON qaiops_logs BEGIN
                INSERT INTO qaiops_logs_fts(rowid, prompt_text, response_text)
                VALUES (NEW.rowid, NEW.prompt_text, NEW.response_text);
            END
            """,
            """
            CREATE TRIGGER IF NOT EXISTS qaiops_logs_ad AFTER DELETE ON qaiops_logs BEGIN
                INSERT INTO qaiops_logs_fts(qaiops_logs_fts, rowid, prompt_text, response_text)
                VALUES ('delete', OLD.rowid, OLD.prompt_text, OLD.response_text);
            END
            """,
            """
            CREATE TRIGGER IF NOT EXISTS qaiops_logs_au AFTER UPDATE ON qaiops_logs BEGIN
                INSERT INTO qaiops_logs_fts(qaiops_logs_fts, rowid, prompt_text, response_text)
                VALUES ('delete', OLD.rowid, OLD.prompt_text, OLD.response_text);
                INSERT INTO qaiops_logs_fts(rowid, prompt_text, response_text)
                VALUES (NEW.rowid, NEW.prompt_text, NEW.response_text);
            END
            """,
        ]:
            await conn.execute(text(trigger_sql))


async def get_session():
    """FastAPI dependency that yields an async DB session."""
    async with async_session() as session:
        yield session
