from __future__ import annotations

import logging
import time
from typing import Optional, Tuple, Union

import cv2
import numpy as np


logger = logging.getLogger(__name__)


class VideoStreamManager:
    def __init__(self, source: Union[int, str], reconnect_delay_sec: float = 2.0) -> None:
        self.source = source
        self.reconnect_delay_sec = reconnect_delay_sec
        self.cap: Optional[cv2.VideoCapture] = None

    def open(self) -> bool:
        self.release()
        self.cap = cv2.VideoCapture(self.source)
        if self.cap is None or not self.cap.isOpened():
            logger.error("Unable to open video source: %s", self.source)
            return False
        logger.info("Video source opened: %s", self.source)
        return True

    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        if self.cap is None or not self.cap.isOpened():
            if not self.open():
                time.sleep(self.reconnect_delay_sec)
                return False, None

        ok, frame = self.cap.read()
        if not ok or frame is None:
            logger.warning("Frame read failed. Trying reconnect in %.1fs", self.reconnect_delay_sec)
            self.release()
            time.sleep(self.reconnect_delay_sec)
            return False, None
        return True, frame

    def release(self) -> None:
        if self.cap is not None:
            self.cap.release()
            self.cap = None
