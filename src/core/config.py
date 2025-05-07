"""
Configuration settings for Overwatch Aim Assist
"""

import win32con
import numpy as np
from typing import Dict, Any

class Config:
    """All configurable parameters of the system"""
    
    # Profile paths
    PROFILES_DIR: str = "profiles"
    DEFAULT_PROFILE: str = "default.json"
    
    # Detection area size (pixels)
    DETECTION_SIZE: int = 256
    
    # Smoothing settings
    BASE_SMOOTHING: float = 0.2          # Base smoothness (0.0-1.0)
    SIZE_SMOOTHING_FACTOR: float = 0.5   # Target size influence on smoothness
    DISTANCE_SMOOTHING_FACTOR: float = 0.3  # Distance influence on smoothness
    VELOCITY_SMOOTHING_FACTOR: float = 0.2  # Velocity influence on smoothness
    
    # Control keys
    ACTIVATION_KEY: int = win32con.VK_MENU  # ALT
    TOGGLE_DEBUG_KEY: int = ord('D')        # D for debug toggle
    EXIT_KEY: int = ord('Q')                # Q for exit
    SAVE_PROFILE_KEY: int = ord('S')        # S for save profile
    LOAD_PROFILE_KEY: int = ord('L')        # L for load profile
    
    # Performance settings
    FPS_LIMIT: int = 60                    # FPS limit
    DEBUG_MODE: bool = True                # Debug mode by default
    
    # Crosshair offset
    VERTICAL_OFFSET: int = 30            # Positive = below center
    
    # Target parameters
    MIN_TARGET_SIZE: int = 50            # Minimum contour area
    MAX_TARGET_AREA: int = 2000          # For size normalization
    TARGET_LOCK_TIME: float = 0.3        # Target hold time (sec)
    
    # Prediction settings
    PREDICTION_ENABLED: bool = True      # Enable movement prediction
    PREDICTION_TIME: float = 0.1         # Prediction time (sec)
    MAX_PREDICTION_DISTANCE: int = 100   # Maximum prediction distance
    
    # Color ranges (HSV)
    LOWER_RED1: np.ndarray = np.array([0, 150, 150])
    UPPER_RED1: np.ndarray = np.array([10, 255, 255])
    LOWER_RED2: np.ndarray = np.array([160, 150, 150])
    UPPER_RED2: np.ndarray = np.array([180, 255, 255])
    
    # Target selection weights
    CENTER_WEIGHT: float = 0.4           # Center screen priority
    SIZE_WEIGHT: float = 0.3             # Target size priority
    CURRENT_TARGET_WEIGHT: float = 0.3   # Current target priority
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Convert settings to dictionary for saving"""
        return {
            'DETECTION_SIZE': cls.DETECTION_SIZE,
            'BASE_SMOOTHING': cls.BASE_SMOOTHING,
            'SIZE_SMOOTHING_FACTOR': cls.SIZE_SMOOTHING_FACTOR,
            'DISTANCE_SMOOTHING_FACTOR': cls.DISTANCE_SMOOTHING_FACTOR,
            'VELOCITY_SMOOTHING_FACTOR': cls.VELOCITY_SMOOTHING_FACTOR,
            'VERTICAL_OFFSET': cls.VERTICAL_OFFSET,
            'MIN_TARGET_SIZE': cls.MIN_TARGET_SIZE,
            'MAX_TARGET_AREA': cls.MAX_TARGET_AREA,
            'TARGET_LOCK_TIME': cls.TARGET_LOCK_TIME,
            'LOWER_RED1': cls.LOWER_RED1.tolist(),
            'UPPER_RED1': cls.UPPER_RED1.tolist(),
            'LOWER_RED2': cls.LOWER_RED2.tolist(),
            'UPPER_RED2': cls.UPPER_RED2.tolist(),
            'CENTER_WEIGHT': cls.CENTER_WEIGHT,
            'SIZE_WEIGHT': cls.SIZE_WEIGHT,
            'CURRENT_TARGET_WEIGHT': cls.CURRENT_TARGET_WEIGHT,
            'PREDICTION_ENABLED': cls.PREDICTION_ENABLED,
            'PREDICTION_TIME': cls.PREDICTION_TIME,
            'MAX_PREDICTION_DISTANCE': cls.MAX_PREDICTION_DISTANCE,
            'FPS_LIMIT': cls.FPS_LIMIT
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> None:
        """Load settings from dictionary"""
        for key, value in data.items():
            if hasattr(cls, key):
                if isinstance(value, list) and key.startswith(('LOWER_', 'UPPER_')):
                    setattr(cls, key, np.array(value))
                else:
                    setattr(cls, key, value) 