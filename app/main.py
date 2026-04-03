import os
from contextlib import asynccontextmanager
from pathlib import Path

import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.socketio_server import sio

# Import all models so SQLAlchemy registers them
import app.models  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create upload directories
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    Path(settings.UPLOAD_DIR + "/avatars").mkdir(parents=True, exist_ok=True)
    Path(settings.UPLOAD_DIR + "/portfolio").mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(
    title="SeuServiço API",
    description="Conecta clientes a prestadores de serviços locais",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(api_router)

# ── Static files (uploads) ────────────────────────────────────────────────────
app.mount(f"/{settings.UPLOAD_DIR}", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# ── Socket.IO ASGI wrapper ────────────────────────────────────────────────────
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)


@app.get("/", tags=["Health"])
def health():
    return {"status": "ok", "service": settings.APP_NAME}


@app.get("/api/v1/categories", tags=["Categories"])
def get_categories():
    from app.core.config import CATEGORIES
    return CATEGORIES
