"""
WebSocket - Real-time communication for execution progress
"""
import asyncio
import json
from typing import Any, Dict, Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections."""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.debug(f"WebSocket connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        logger.debug(f"WebSocket disconnected. Total: {len(self.active_connections)}")

    async def send_message(self, websocket: WebSocket, message: Dict[str, Any]):
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.warning(f"Failed to send WebSocket message: {e}")

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients."""
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.add(connection)

        for conn in disconnected:
            self.active_connections.discard(conn)


manager = ConnectionManager()


def get_connection_manager() -> ConnectionManager:
    """Get the global connection manager."""
    return manager


@router.websocket("/execution")
async def execution_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time execution progress."""
    await manager.connect(websocket)

    try:
        # Send initial connected message
        await manager.send_message(websocket, {
            "type": "connected",
            "message": "WebSocket 连接成功",
        })

        while True:
            # Wait for messages from client
            data = await websocket.receive_json()
            message_type = data.get("type")

            if message_type == "ping":
                await manager.send_message(websocket, {"type": "pong"})

            elif message_type == "execute":
                # Handle execution request via WebSocket
                await handle_ws_execution(websocket, data)

            elif message_type == "screenshot":
                # Return current screenshot
                from app.services.screenshot_service import ScreenshotService
                ss = ScreenshotService()
                screenshot = ss.take_screenshot_base64()
                await manager.send_message(websocket, {
                    "type": "screenshot",
                    "data": screenshot,
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


async def handle_ws_execution(websocket: WebSocket, data: Dict[str, Any]):
    """Handle execution request over WebSocket."""
    from app.models.instruction import InstructionRequest
    from app.services.instruction_parser import InstructionParser
    from app.services.llm_service import LLMService
    from app.services.access_automation import AccessAutomation

    instruction = data.get("instruction", "")
    provider = data.get("provider")
    model = data.get("model")

    llm_svc = LLMService()
    parser = InstructionParser()
    auto = AccessAutomation()

    try:
        # Step 1: Parse instruction
        await manager.send_message(websocket, {
            "type": "progress",
            "stage": "parsing",
            "message": "正在解析指令...",
            "progress": 10,
        })

        llm_response = await llm_svc.parse_instruction(
            instruction=instruction,
            provider=provider,
            model=model,
        )
        parsed = parser.parse(llm_response)

        await manager.send_message(websocket, {
            "type": "progress",
            "stage": "parsed",
            "message": f"指令解析完成: {parsed.description}",
            "progress": 30,
            "parsed": parsed.model_dump(),
        })

        # Step 2: Execute steps
        steps = parser.to_operation_steps(parsed)
        total = len(steps)

        def progress_callback(info: Dict[str, Any]):
            asyncio.create_task(manager.send_message(websocket, {
                "type": "progress",
                "stage": "executing",
                "message": info.get("message", ""),
                "progress": 30 + int(60 * info.get("step", 0) / max(info.get("total", 1), 1)),
                "screenshot": info.get("screenshot"),
            }))

        auto.set_progress_callback(progress_callback)
        result = await auto.execute_steps(steps)

        # Step 3: Done
        await manager.send_message(websocket, {
            "type": "complete",
            "stage": "done",
            "message": "执行完成" if result.success else "执行失败",
            "progress": 100,
            "success": result.success,
            "result": result.model_dump(),
        })

    except Exception as e:
        logger.error(f"WebSocket execution error: {e}")
        await manager.send_message(websocket, {
            "type": "error",
            "message": f"执行失败: {str(e)}",
        })


async def broadcast_progress(message: Dict[str, Any]):
    """Broadcast a progress update to all connected clients."""
    await manager.broadcast(message)
