from __future__ import annotations

import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.telemetry_state import SharedState


router = APIRouter()


@router.websocket("/ws/telemetry")
async def telemetry_socket(websocket: WebSocket) -> None:
    await websocket.accept()
    state: SharedState = websocket.app.state.shared_state
    interval: float = websocket.app.state.settings.telemetry_interval_sec

    try:
        while True:
            await websocket.send_json(state.get_telemetry())
            await asyncio.sleep(interval)
    except WebSocketDisconnect:
        return
