"""WebSocket broadcast manager for real-time log streaming."""

import asyncio
import json
from typing import Any

from fastapi import WebSocket


class BroadcastManager:
    """Manages WebSocket connections and broadcasts new logs."""

    def __init__(self):
        self._connections: list[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        async with self._lock:
            self._connections.append(ws)

    async def disconnect(self, ws: WebSocket) -> None:
        async with self._lock:
            if ws in self._connections:
                self._connections.remove(ws)

    async def broadcast(self, data: dict[str, Any]) -> None:
        """Send data to all connected clients, removing dead connections."""
        message = json.dumps(data)
        dead: list[WebSocket] = []

        async with self._lock:
            connections = list(self._connections)

        for ws in connections:
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)

        if dead:
            async with self._lock:
                for ws in dead:
                    if ws in self._connections:
                        self._connections.remove(ws)

    @property
    def connection_count(self) -> int:
        return len(self._connections)


# Singleton instance
broadcast_manager = BroadcastManager()
