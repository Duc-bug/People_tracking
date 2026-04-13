from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.api.telemetry import router as telemetry_router
from app.api.video import router as video_router
from app.config import Settings, get_settings
from app.core.telemetry_state import SharedState
from app.services.pipeline_service import PipelineService
from app.utils.logger import configure_logging


configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings: Settings = get_settings()
    shared_state = SharedState()
    pipeline = PipelineService(settings=settings, state=shared_state)

    app.state.settings = settings
    app.state.shared_state = shared_state
    app.state.pipeline = pipeline

    pipeline.start()
    yield
    pipeline.stop()


app = FastAPI(
    title="Real-time People Tracking & Counting",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(video_router)
app.include_router(telemetry_router)


@app.get("/")
def home() -> FileResponse:
    return FileResponse("static/index.html")
