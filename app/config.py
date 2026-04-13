from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Union


BASE_DIR = Path(__file__).resolve().parents[1]


def _parse_source(value: str) -> Union[int, str]:
    """Parse video source from env to int for webcam or str for URI/path."""
    if value.isdigit():
        return int(value)
    return value


@dataclass(frozen=True)
class Settings:
    model_path: str
    video_source: Union[int, str]
    conf_threshold: float
    iou_threshold: float
    line_position_ratio: float
    reconnect_delay_sec: float
    jpeg_quality: int
    telemetry_interval_sec: float


def get_settings() -> Settings:
    model_default = str(BASE_DIR / "models" / "yolov8n.onnx")
    source_default = "0"

    return Settings(
        model_path=os.getenv("MODEL_PATH", model_default),
        video_source=_parse_source(os.getenv("VIDEO_SOURCE", source_default)),
        conf_threshold=float(os.getenv("CONF_THRESHOLD", "0.35")),
        iou_threshold=float(os.getenv("IOU_THRESHOLD", "0.45")),
        line_position_ratio=float(os.getenv("LINE_POSITION_RATIO", "0.50")),
        reconnect_delay_sec=float(os.getenv("RECONNECT_DELAY_SEC", "2.0")),
        jpeg_quality=int(os.getenv("JPEG_QUALITY", "80")),
        telemetry_interval_sec=float(os.getenv("TELEMETRY_INTERVAL_SEC", "0.25")),
    )
