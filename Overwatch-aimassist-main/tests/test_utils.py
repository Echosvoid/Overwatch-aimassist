"""
Test utilities for Overwatch Aim Assist
"""

import numpy as np
import cv2
from typing import Tuple, List
from src.core.config import Config

def create_test_frame(target_positions: List[Tuple[int, int, float]]) -> np.ndarray:
    """
    Create a test frame with target markers
    
    Args:
        target_positions: List of (x, y, size) tuples for target positions
        
    Returns:
        Test frame with target markers
    """
    frame = np.zeros((Config.DETECTION_SIZE, Config.DETECTION_SIZE, 3), dtype=np.uint8)
    
    # Sort targets by size in descending order to draw larger targets first
    target_positions = sorted(target_positions, key=lambda x: x[2], reverse=True)
    
    for x, y, size in target_positions:
        # Create red target marker with exact area
        side = int(np.sqrt(size))  # Square root of area for square target
        half_side = side // 2
        x1 = max(0, x - half_side)
        y1 = max(0, y - half_side)
        x2 = min(Config.DETECTION_SIZE - 1, x + half_side)
        y2 = min(Config.DETECTION_SIZE - 1, y + half_side)
        
        # Draw target only if it doesn't overlap with existing targets
        target_area = frame[y1:y2+1, x1:x2+1]
        if not np.any(target_area > 0):
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), -1)  # Fill rectangle
        
    return frame

def simulate_target_movement(start_pos: Tuple[int, int],
                           velocity: Tuple[float, float],
                           duration: float,
                           fps: float = 60) -> List[Tuple[int, int, float]]:
    """
    Simulate target movement over time
    
    Args:
        start_pos: Initial (x, y) position
        velocity: (vx, vy) velocity in pixels per second
        duration: Duration in seconds
        fps: Frames per second
        
    Returns:
        List of (x, y, size) positions over time
    """
    positions = []
    dt = 1.0 / fps
    x, y = start_pos
    vx, vy = velocity
    
    for _ in range(int(duration * fps)):
        x += vx * dt
        y += vy * dt
        positions.append((int(x), int(y), 50))  # Fixed size for simplicity
        
    return positions

def create_test_profile(name: str, settings: dict) -> None:
    """
    Create a test profile with given settings
    
    Args:
        name: Profile name
        settings: Dictionary of settings
    """
    import json
    import os
    
    if not os.path.exists(Config.PROFILES_DIR):
        os.makedirs(Config.PROFILES_DIR)
        
    profile_path = os.path.join(Config.PROFILES_DIR, f"{name}.json")
    with open(profile_path, 'w') as f:
        json.dump(settings, f, indent=4) 