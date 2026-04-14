"""QaiOps Log Server — FastAPI application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from qaiops.db.engine import init_db
from qaiops.server.routers import logs, stats


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle."""
    await init_db()
    yield


app = FastAPI(
    title="QaiOps",
    version="0.1.0",
    description="AI CLI Observability — Log Server",
    lifespan=lifespan,
)

# CORS (로컬 대시보드 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(logs.router, prefix="/api/v1", tags=["logs"])
app.include_router(stats.router, prefix="/api/v1", tags=["stats"])


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "version": "0.1.0"}
