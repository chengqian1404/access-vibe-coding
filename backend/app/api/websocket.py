import asyncio
import json
import threading
from typing import Any, Dict, List

from fastapi import WebSocket
from app.utils.logger import logger


class ConnectionManager:
    """Manages active WebSocket connections and broadcasts messages."""

    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []
        self._lock = threading.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        with self._lock:
            self.active_connections.append(websocket)
        logger.info("WebSocket client connected. Total: %d", len(self.active_connections))

    def disconnect(self, websocket: WebSocket) -> None:
        with self._lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
        logger.info("WebSocket client disconnected. Total: %d", len(self.active_connections))

    async def broadcast(self, message: Dict[str, Any]) -> None:
        payload = json.dumps(message, ensure_ascii=False)
        dead: List[WebSocket] = []
        with self._lock:
            connections = list(self.active_connections)
        for ws in connections:
            try:
                await ws.send_text(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)

    async def send_to(self, websocket: WebSocket, message: Dict[str, Any]) -> None:
        try:
            await websocket.send_text(json.dumps(message, ensure_ascii=False))
        except Exception as exc:
            logger.warning("Failed to send message to client: %s", exc)
            self.disconnect(websocket)

    def broadcast_sync(self, message: Dict[str, Any]) -> None:
        """Thread-safe synchronous broadcast – posts to the running event loop."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.ensure_future(self.broadcast(message))
            else:
                loop.run_until_complete(self.broadcast(message))
        except Exception as exc:
            logger.debug("broadcast_sync error: %s", exc)


manager = ConnectionManager()
