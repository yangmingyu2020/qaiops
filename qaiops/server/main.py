"""QaiOps Log Server -- FastAPI application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from qaiops.db.engine import init_db
from qaiops.server.broadcast import broadcast_manager
from qaiops.server.routers import logs, stats


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle."""
    await init_db()
    yield


app = FastAPI(
    title="QaiOps",
    version="0.2.0",
    description="AI CLI Observability -- Log Server",
    lifespan=lifespan,
)

# CORS
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
    return {
        "status": "ok",
        "version": "0.2.0",
        "ws_clients": broadcast_manager.connection_count,
    }


@app.websocket("/ws/live")
async def websocket_live(ws: WebSocket):
    """Real-time log streaming via WebSocket."""
    await broadcast_manager.connect(ws)
    try:
        while True:
            # Keep connection alive, listen for client pings
            await ws.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        await broadcast_manager.disconnect(ws)
