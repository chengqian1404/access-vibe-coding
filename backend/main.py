"""
Access Vibe Coding - FastAPI Backend Entry Point
"""
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.api.routes import router as api_router
from app.api.websocket import router as ws_router
from app.config.settings import get_settings

settings = get_settings()

app = FastAPI(
    title="Access Vibe Coding API",
    description="Backend API for Access Vibe Coding - AI-powered Microsoft Access automation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix="/api/v1")
app.include_router(ws_router, prefix="/ws")


@app.on_event("startup")
async def startup_event():
    logger.info(f"Access Vibe Coding Backend starting on port {settings.PORT}")
    logger.info(f"Docs available at http://localhost:{settings.PORT}/docs")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Access Vibe Coding Backend shutting down")


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )
