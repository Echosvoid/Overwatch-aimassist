"""Type definitions for the Overwatch Aim Assist project."""

from typing import TypedDict, List, Tuple, Optional, Union, Dict, Any
import numpy as np

# Basic types
Point = Tuple[int, int]
Vector = Tuple[float, float]
Color = Tuple[int, int, int]
Frame = np.ndarray

class Target(TypedDict):
    """Represents a detected target in the game."""
    position: Point
    size: int
    confidence: float
    velocity: Optional[Vector]
    class_id: int

class AimState(TypedDict):
    """Represents the current state of aim assistance."""
    enabled: bool
    current_target: Optional[Target]
    last_position: Point
    current_velocity: Vector
    smoothing_factor: float

class Profile(TypedDict):
    """Represents a user profile with settings."""
    name: str
    sensitivity: float
    smoothing: float
    prediction: bool
    target_priority: str
    custom_settings: Dict[str, Any]

class DetectionConfig(TypedDict):
    """Configuration for target detection."""
    confidence_threshold: float
    min_target_size: int
    max_target_distance: int
    detection_frequency: int

class AimConfig(TypedDict):
    """Configuration for aim assistance."""
    smoothing_factor: float
    prediction_time: float
    max_angle_correction: float
    enable_prediction: bool

class PerformanceConfig(TypedDict):
    """Configuration for performance settings."""
    use_gpu: bool
    processing_resolution: float
    frame_skip: int
    debug_mode: bool

class Config(TypedDict):
    """Main configuration type."""
    sensitivity: Dict[str, float]
    target_detection: DetectionConfig
    aim_assistance: AimConfig
    performance: PerformanceConfig
    controls: Dict[str, str]
    profiles: Dict[str, Profile] 