from __future__ import annotations

from typing import Dict, Iterable, Tuple


class LineCounter:
    """
    Crossing logic:
    - Move from above line to below line: IN
    - Move from below line to above line: OUT
    """

    def __init__(self, line_y: int) -> None:
        self.line_y = line_y
        self.previous_side: Dict[int, bool] = {}
        self.total_in = 0
        self.total_out = 0
        self.current_count = 0

    def update(self, track_centers: Dict[int, Tuple[int, int]], active_track_ids: Iterable[int]) -> Dict[str, int]:
        for track_id, (_cx, cy) in track_centers.items():
            is_below_line = cy >= self.line_y
            if track_id in self.previous_side:
                old_side = self.previous_side[track_id]
                if old_side != is_below_line:
                    if old_side is False and is_below_line is True:
                        self.total_in += 1
                    elif old_side is True and is_below_line is False:
                        self.total_out += 1
            self.previous_side[track_id] = is_below_line

        self.current_count = len(set(active_track_ids))
        return {
            "total_in": self.total_in,
            "total_out": self.total_out,
            "current_count": self.current_count,
        }
