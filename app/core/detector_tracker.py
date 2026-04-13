from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence, Tuple

import numpy as np
from ultralytics import YOLO


logger = logging.getLogger(__name__)


@dataclass
class TrackedPerson:
    track_id: int
    bbox: Tuple[int, int, int, int]
    confidence: float
    center: Tuple[int, int]


class DetectorTracker:
    def __init__(
        self,
        model_path: str,
        conf_threshold: float = 0.35,
        iou_threshold: float = 0.45,
    ) -> None:
        if not Path(model_path).exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")

        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        # Explicit task avoids "guess model task" warning for ONNX models.
        self.model = YOLO(model_path, task="detect")
        logger.info("YOLO model loaded: %s", model_path)

    def infer(self, frame: np.ndarray) -> Tuple[List[TrackedPerson], Sequence[int]]:
        results = self.model.track(
            source=frame,
            conf=self.conf_threshold,
            iou=self.iou_threshold,
            classes=[0],  # person class only
            persist=True,
            tracker="bytetrack.yaml",
            verbose=False,
        )

        if not results:
            return [], []

        result = results[0]
        boxes = result.boxes
        if boxes is None or boxes.xyxy is None:
            return [], []

        xyxy = boxes.xyxy.cpu().numpy().astype(int)
        confs = boxes.conf.cpu().numpy() if boxes.conf is not None else np.zeros((len(xyxy),), dtype=float)
        ids = boxes.id.int().cpu().tolist() if boxes.id is not None else [None] * len(xyxy)

        tracked: List[TrackedPerson] = []
        for box, conf, track_id in zip(xyxy, confs, ids):
            if track_id is None:
                continue
            x1, y1, x2, y2 = box.tolist()
            center = ((x1 + x2) // 2, (y1 + y2) // 2)
            tracked.append(
                TrackedPerson(
                    track_id=int(track_id),
                    bbox=(x1, y1, x2, y2),
                    confidence=float(conf),
                    center=center,
                )
            )

        active_ids = [item.track_id for item in tracked]
        return tracked, active_ids
