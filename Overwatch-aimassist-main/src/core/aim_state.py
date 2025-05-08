"""
Aim state tracking for Overwatch Aim Assist
"""

import time
from typing import Tuple, Optional
from src.core.config import Config

class AimState:
    """Tracks aiming state between frames"""
    
    def __init__(self):
        self.current_target: Optional[Tuple[int, int, float]] = None
        self.last_target_time: float = 0
        self.last_target_pos: Tuple[int, int] = (0, 0)
        self.target_velocity: Tuple[float, float] = (0, 0)
        self.screen_center: Tuple[int, int] = (
            Config.DETECTION_SIZE // 2, 
            Config.DETECTION_SIZE // 2
        )
        self.last_update_time: float = time.time() 