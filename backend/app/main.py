import json
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.api.websocket import manager
from app.config.settings import settings
from app.utils.logger import logger, set_ws_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──────────────────────────────────────────────────────
    logger.info("Starting Live Stream Learning Analyzer backend v1.0.0")

    # Ensure storage directories exist
    for path in (settings.STORAGE_PATH, settings.RECORDINGS_PATH, settings.ANALYSES_PATH, settings.CACHE_PATH):
        Path(path).mkdir(parents=True, exist_ok=True)

    # Initialise database
    _init_db()

    # Wire WebSocket manager into the logger so logs stream to frontend
    set_ws_manager(manager)

    logger.info("Backend startup complete. Listening on %s:%d", settings.HOST, settings.PORT)
    yield

    # ── Shutdown ─────────────────────────────────────────────────────
    logger.info("Shutting down backend…")


def _init_db() -> None:
    from sqlalchemy import create_engine
    from app.models.recording import Base as RecordingBase
    from app.models.analysis import Analysis  # noqa: F401 – registers models
    from app.models.config import AppConfig   # noqa: F401

    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False,
    )
    RecordingBase.metadata.create_all(bind=engine)
    logger.info("Database initialised: %s", settings.DATABASE_URL)


app = FastAPI(
    title="Live Stream Learning Analyzer",
    description="直播学习分析器后端 API",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── REST API routes ───────────────────────────────────────────────────
app.include_router(router)


# ── WebSocket endpoint ────────────────────────────────────────────────
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            raw = await websocket.receive_text()
            try:
                msg = json.loads(raw)
                msg_type = msg.get("type", "")
                if msg_type == "ping":
                    await manager.send_to(websocket, {"type": "pong", "data": {}})
                elif msg_type == "get_status":
                    from app.api.routes import _screen_recorder, _audio_recorder, _monitor_service, _current_recording
                    await manager.send_to(websocket, {
                        "type": "status",
                        "data": {
                            "screen": _screen_recorder.get_status(),
                            "audio": _audio_recorder.get_status(),
                            "monitor": _monitor_service.get_status(),
                            "current_recording": _current_recording,
                        },
                    })
            except json.JSONDecodeError:
                logger.warning("Received non-JSON WebSocket message")
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ── Static files (production frontend) ────────────────────────────────
_frontend_path = Path(__file__).resolve().parent.parent.parent.parent / "frontend" / "dist"
if _frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(_frontend_path), html=True), name="frontend")
    logger.info("Serving frontend from %s", _frontend_path)


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info",
    )
