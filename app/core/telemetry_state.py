from __future__ import annotations

from threading import Lock
from typing import Any, Dict, Optional


class SharedState:
    def __init__(self) -> None:
        self._lock = Lock()
        self._latest_jpeg: Optional[bytes] = None
        self._telemetry: Dict[str, Any] = {
            "fps": 0.0,
            "total_in": 0,
            "total_out": 0,
            "current_count": 0,
            "tracking_ids": [],
            "status": "initializing",
        }

    def set_frame(self, jpg_bytes: bytes) -> None:
        with self._lock:
            self._latest_jpeg = jpg_bytes

    def get_frame(self) -> Optional[bytes]:
        with self._lock:
            return self._latest_jpeg

    def set_telemetry(self, payload: Dict[str, Any]) -> None:
        with self._lock:
            self._telemetry = payload

    def get_telemetry(self) -> Dict[str, Any]:
        with self._lock:
            return dict(self._telemetry)
