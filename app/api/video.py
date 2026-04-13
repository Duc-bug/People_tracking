from __future__ import annotations

import time
from typing import Generator

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.core.telemetry_state import SharedState


router = APIRouter()


def _mjpeg_generator(state: SharedState) -> Generator[bytes, None, None]:
    boundary = b"--frame\r\n"
    while True:
        frame = state.get_frame()
        if frame is None:
            time.sleep(0.05)
            continue

        yield (
            boundary
            + b"Content-Type: image/jpeg\r\n\r\n"
            + frame
            + b"\r\n"
        )
        time.sleep(0.001)


@router.get("/video_feed")
def video_feed(request: Request) -> StreamingResponse:
    state: SharedState = request.app.state.shared_state
    return StreamingResponse(
        _mjpeg_generator(state),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )
