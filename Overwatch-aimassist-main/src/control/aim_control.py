"""Aim control module for Overwatch Aim Assist.

This module handles the aim assistance functionality, including:
- Calculating aim vectors
- Applying smoothing
- Predicting target movement
- Managing aim state
"""

import win32api
import win32con
import numpy as np
from typing import Optional, Tuple
from math import sqrt
from src.core.config import Config
from src.core.aim_state import AimState
from ..types import Target, Point, Vector

def is_activated() -> bool:
    """Check if activation key is pressed"""
    return win32api.GetAsyncKeyState(Config.ACTIVATION_KEY) < 0

def calculate_target_velocity(current_pos: Tuple[int, int], 
                            last_pos: Tuple[int, int],
                            dt: float) -> Tuple[float, float]:
    """Calculate target movement velocity"""
    if dt <= 0:
        return (0, 0)
    return ((current_pos[0] - last_pos[0]) / dt,
            (current_pos[1] - last_pos[1]) / dt)

def predict_target_position(current_pos: Tuple[int, int],
                          velocity: Tuple[float, float],
                          prediction_time: float) -> Tuple[int, int]:
    """Predict future target position"""
    if not Config.PREDICTION_ENABLED or prediction_time <= 0:
        return current_pos
        
    predicted_x = current_pos[0] + velocity[0] * prediction_time
    predicted_y = current_pos[1] + velocity[1] * prediction_time
    
    # Limit maximum prediction distance
    dx = predicted_x - current_pos[0]
    dy = predicted_y - current_pos[1]
    distance = sqrt(dx*dx + dy*dy)
    
    if distance > Config.MAX_PREDICTION_DISTANCE:
        scale = Config.MAX_PREDICTION_DISTANCE / distance
        predicted_x = current_pos[0] + dx * scale
        predicted_y = current_pos[1] + dy * scale
    
    return (int(predicted_x), int(predicted_y))

def adaptive_smoothing(target_size: float, 
                      distance: float,
                      velocity: float) -> float:
    """
    Calculate adaptive smoothing value based on:
    - Target size
    - Distance to target
    - Target movement velocity
    """
    size_factor = min(target_size / Config.MAX_TARGET_AREA, 1.0)
    distance_factor = min(distance / Config.DETECTION_SIZE, 1.0)
    velocity_factor = min(velocity / 1000, 1.0)  # Velocity normalization
    
    smoothing = Config.BASE_SMOOTHING
    smoothing *= (1 - Config.SIZE_SMOOTHING_FACTOR * size_factor)
    smoothing *= (1 + Config.DISTANCE_SMOOTHING_FACTOR * distance_factor)
    smoothing *= (1 + Config.VELOCITY_SMOOTHING_FACTOR * velocity_factor)
    
    return max(0.1, min(1.0, smoothing))  # Limit to reasonable range

def move_crosshair(x_offset: int, y_offset: int, target_size: float, aim_state: AimState) -> None:
    """
    Smoothly move cursor with adaptive smoothing
    
    Args:
        x_offset: X offset from center
        y_offset: Y offset from center
        target_size: Target area for adaptive smoothing
        aim_state: Current aim state for velocity calculation
    """
    distance = sqrt(x_offset*x_offset + y_offset*y_offset)
    velocity = sqrt(aim_state.target_velocity[0]**2 + aim_state.target_velocity[1]**2)
    
    smoothing = adaptive_smoothing(target_size, distance, velocity)
    
    win32api.mouse_event(
        win32con.MOUSEEVENTF_MOVE,
        int(x_offset * smoothing),
        int(y_offset * smoothing),
        0, 0
    )

class AimController:
    """Handles aim assistance functionality.
    
    This class is responsible for:
    - Calculating optimal aim vectors
    - Applying aim smoothing
    - Predicting target movement
    - Managing aim state
    """

    def __init__(self, config: dict) -> None:
        """Initialize the aim controller.
        
        Args:
            config: Configuration dictionary containing aim parameters
        """
        self.smoothing_factor = config['aim_assistance']['smoothing_factor']
        self.prediction_time = config['aim_assistance']['prediction_time']
        self.max_angle_correction = config['aim_assistance']['max_angle_correction']
        self.enable_prediction = config['aim_assistance']['enable_prediction']
        
        # Initialize aim state
        self.aim_state: AimState = {
            'enabled': False,
            'current_target': None,
            'last_position': (0, 0),
            'current_velocity': (0.0, 0.0),
            'smoothing_factor': self.smoothing_factor
        }

    def calculate_aim_vector(self, current_pos: Point, target_pos: Point) -> Vector:
        """Calculate aim vector from current position to target.
        
        Args:
            current_pos: Current aim position
            target_pos: Target position
            
        Returns:
            Aim vector as (x, y) tuple
        """
        dx = target_pos[0] - current_pos[0]
        dy = target_pos[1] - current_pos[1]
        
        # Calculate distance
        distance = np.sqrt(dx**2 + dy**2)
        
        # Normalize vector
        if distance > 0:
            dx /= distance
            dy /= distance
            
        return (dx, dy)

    def apply_smoothing(self, vector: Vector) -> Vector:
        """Apply smoothing to aim movement.
        
        Args:
            vector: Raw aim vector
            
        Returns:
            Smoothed aim vector
        """
        # Get current velocity
        current_vx, current_vy = self.aim_state['current_velocity']
        
        # Calculate vector magnitude
        magnitude = sqrt(vector[0]**2 + vector[1]**2)
        
        # Dynamic smoothing based on movement speed
        if magnitude > 0.5:  # Fast movement
            smoothing = self.smoothing_factor * 0.8  # More responsive
        else:
            smoothing = self.smoothing_factor  # Normal smoothing
        
        # Apply smoothing
        smoothed_vx = current_vx + (vector[0] - current_vx) * smoothing
        smoothed_vy = current_vy + (vector[1] - current_vy) * smoothing
        
        # Update state
        self.aim_state['current_velocity'] = (smoothed_vx, smoothed_vy)
        
        return (smoothed_vx, smoothed_vy)

    def predict_target_position(self, target: Target, current_pos: Point) -> Point:
        """Predict target position based on current movement.
        
        Args:
            target: Current target
            current_pos: Current aim position
            
        Returns:
            Predicted target position
        """
        if not self.enable_prediction or not target['velocity']:
            return target['position']
            
        # Get current position and velocity
        pos_x, pos_y = target['position']
        vel_x, vel_y = target['velocity']
        
        # Calculate acceleration with dampening
        if hasattr(self, 'last_velocity'):
            acc_x = (vel_x - self.last_velocity[0]) / self.prediction_time
            acc_y = (vel_y - self.last_velocity[1]) / self.prediction_time
            
            # Dampen acceleration for sudden changes
            acc_magnitude = sqrt(acc_x*acc_x + acc_y*acc_y)
            if acc_magnitude > 1000:  # Threshold for sudden acceleration
                dampening = 1000 / acc_magnitude
                acc_x *= dampening
                acc_y *= dampening
        else:
            acc_x = acc_y = 0
            
        # Store current velocity for next frame
        self.last_velocity = (vel_x, vel_y)
        
        # Predict position with dampened acceleration
        pred_x = pos_x + vel_x * self.prediction_time + 0.5 * acc_x * self.prediction_time**2
        pred_y = pos_y + vel_y * self.prediction_time + 0.5 * acc_y * self.prediction_time**2
        
        # Limit prediction distance with smooth falloff
        dx = pred_x - pos_x
        dy = pred_y - pos_y
        distance = sqrt(dx*dx + dy*dy)
        if distance > Config.MAX_PREDICTION_DISTANCE:
            # Smooth falloff instead of hard cutoff
            falloff = (Config.MAX_PREDICTION_DISTANCE / distance) ** 2
            pred_x = pos_x + dx * falloff
            pred_y = pos_y + dy * falloff
        
        return (int(pred_x), int(pred_y))

    def update_aim_state(self, target: Optional[Target], current_pos: Point) -> None:
        """Update the current aim state.
        
        Args:
            target: Current target (if any)
            current_pos: Current aim position
        """
        self.aim_state['current_target'] = target
        self.aim_state['last_position'] = current_pos

    def get_aim_correction(self, current_pos: Point, target: Target) -> Vector:
        """Calculate aim correction for the current target.
        
        Args:
            current_pos: Current aim position
            target: Target to aim at
            
        Returns:
            Aim correction vector
        """
        # Predict target position
        predicted_pos = self.predict_target_position(target, current_pos)
        
        # Calculate aim vector
        aim_vector = self.calculate_aim_vector(current_pos, predicted_pos)
        
        # Apply smoothing
        smoothed_vector = self.apply_smoothing(aim_vector)
        
        # Apply angle correction limit
        magnitude = np.sqrt(smoothed_vector[0]**2 + smoothed_vector[1]**2)
        if magnitude > 0:
            max_correction = np.tan(np.radians(self.max_angle_correction))
            if magnitude > max_correction:
                scale = max_correction / magnitude
                smoothed_vector = (smoothed_vector[0] * scale, smoothed_vector[1] * scale)
        
        return smoothed_vector

    def toggle_aim_assist(self) -> None:
        """Toggle aim assistance on/off."""
        self.aim_state['enabled'] = not self.aim_state['enabled']
        
    def is_enabled(self) -> bool:
        """Check if aim assistance is enabled.
        
        Returns:
            True if aim assistance is enabled
        """
        return self.aim_state['enabled'] 