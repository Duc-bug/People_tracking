from __future__ import annotations

from typing import Dict, Iterable

import cv2
import numpy as np

from app.core.detector_tracker import TrackedPerson


def draw_annotations(
    frame: np.ndarray,
    tracks: Iterable[TrackedPerson],
    line_y: int,
    fps: float,
    counts: Dict[str, int],
) -> np.ndarray:
    annotated = frame.copy()
    h, w = annotated.shape[:2]

    cv2.line(annotated, (0, line_y), (w, line_y), (0, 255, 255), 2)

    for item in tracks:
        x1, y1, x2, y2 = item.bbox
        cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 200, 0), 2)
        label = f"ID {item.track_id} | {item.confidence:.2f}"
        cv2.putText(
            annotated,
            label,
            (x1, max(20, y1 - 8)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 200, 0),
            2,
            cv2.LINE_AA,
        )

    cv2.putText(
        annotated,
        f"FPS: {fps:.1f}",
        (10, 25),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )
    cv2.putText(
        annotated,
        f"IN: {counts['total_in']}  OUT: {counts['total_out']}  CURRENT: {counts['current_count']}",
        (10, h - 14),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )
    return annotated
