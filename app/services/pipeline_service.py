from __future__ import annotations

import logging
import threading
import time
from typing import Optional

import cv2

from app.config import Settings
from app.core.counter import LineCounter
from app.core.detector_tracker import DetectorTracker
from app.core.stream_manager import VideoStreamManager
from app.core.telemetry_state import SharedState
from app.core.visualizer import draw_annotations
from app.utils.time_utils import FPSMeter


logger = logging.getLogger(__name__)


class PipelineService:
    def __init__(self, settings: Settings, state: SharedState) -> None:
        self.settings = settings
        self.state = state

        self.stream = VideoStreamManager(
            source=self.settings.video_source,
            reconnect_delay_sec=self.settings.reconnect_delay_sec,
        )
        self.detector = DetectorTracker(
            model_path=self.settings.model_path,
            conf_threshold=self.settings.conf_threshold,
            iou_threshold=self.settings.iou_threshold,
        )
        self.counter: Optional[LineCounter] = None
        self.fps_meter = FPSMeter()

        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, name="pipeline-thread", daemon=True)
        self._thread.start()
        logger.info("Pipeline thread started")

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)
        self.stream.release()
        logger.info("Pipeline thread stopped")

    def _ensure_counter(self, frame_height: int) -> None:
        if self.counter is None:
            line_y = int(frame_height * self.settings.line_position_ratio)
            self.counter = LineCounter(line_y=line_y)
            logger.info("Counter initialized with line_y=%d", line_y)

    def _run(self) -> None:
        while not self._stop_event.is_set():
            try:
                ok, frame = self.stream.read()
                if not ok or frame is None:
                    self.state.set_telemetry(
                        {
                            "fps": 0.0,
                            "total_in": self.counter.total_in if self.counter else 0,
                            "total_out": self.counter.total_out if self.counter else 0,
                            "current_count": 0,
                            "tracking_ids": [],
                            "status": "waiting_for_stream",
                            "timestamp": time.time(),
                        }
                    )
                    continue

                self._ensure_counter(frame.shape[0])
                assert self.counter is not None

                tracks, active_ids = self.detector.infer(frame)
                track_centers = {item.track_id: item.center for item in tracks}
                counts = self.counter.update(track_centers=track_centers, active_track_ids=active_ids)
                fps = self.fps_meter.update()

                annotated = draw_annotations(
                    frame=frame,
                    tracks=tracks,
                    line_y=self.counter.line_y,
                    fps=fps,
                    counts=counts,
                )

                ok_jpg, encoded = cv2.imencode(
                    ".jpg",
                    annotated,
                    [int(cv2.IMWRITE_JPEG_QUALITY), self.settings.jpeg_quality],
                )
                if ok_jpg:
                    self.state.set_frame(encoded.tobytes())

                self.state.set_telemetry(
                    {
                        "fps": round(fps, 2),
                        "total_in": counts["total_in"],
                        "total_out": counts["total_out"],
                        "current_count": counts["current_count"],
                        "tracking_ids": sorted(set(active_ids)),
                        "status": "running",
                        "timestamp": time.time(),
                    }
                )
            except Exception:
                logger.exception("Unexpected error in pipeline loop")
                self.state.set_telemetry(
                    {
                        "fps": 0.0,
                        "total_in": self.counter.total_in if self.counter else 0,
                        "total_out": self.counter.total_out if self.counter else 0,
                        "current_count": 0,
                        "tracking_ids": [],
                        "status": "error",
                        "timestamp": time.time(),
                    }
                )
                time.sleep(0.5)
