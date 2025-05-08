"""Target detection module for Overwatch Aim Assist.

This module handles the detection and tracking of targets in the game screen.
It uses computer vision techniques to identify potential targets and track their movement.
"""

import cv2
import numpy as np
from typing import List, Optional, Tuple
from math import sqrt
from src.core.config import Config
from ..types import Target, Frame, Point, Vector

def calculate_distance(p1: Tuple[int, int], p2: Tuple[int, int]) -> float:
    """Calculate Euclidean distance between two points"""
    return sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def create_target_mask(frame: np.ndarray) -> np.ndarray:
    """Create mask of potential targets by color"""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask1 = cv2.inRange(hsv, Config.LOWER_RED1, Config.UPPER_RED1)
    mask2 = cv2.inRange(hsv, Config.LOWER_RED2, Config.UPPER_RED2)
    return cv2.bitwise_or(mask1, mask2)

def extract_targets(mask: np.ndarray) -> List[Tuple[int, int, float]]:
    """Extract centers and areas of all valid targets"""
    # Find contours with hierarchy to handle nested contours
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    targets = []
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > Config.MIN_TARGET_SIZE:
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                # Check if point is within detection area
                if 0 <= cx < Config.DETECTION_SIZE and 0 <= cy < Config.DETECTION_SIZE:
                    targets.append((cx, cy, area))
    
    # Sort targets by area in descending order
    targets.sort(key=lambda x: x[2], reverse=True)
    return targets

def calculate_target_score(target: Tuple[int, int, float],
                          center: Tuple[int, int],
                          current_target: Optional[Tuple[int, int, float]]) -> float:
    """
    Calculate target rating based on:
    1. Proximity to center
    2. Target size
    3. Proximity to current target
    """
    cx, cy, area = target
    
    # Center proximity
    center_dist = calculate_distance((cx, cy), center)
    center_score = 1 / (1 + center_dist)
    
    # Target size (normalized)
    size_score = min(area / Config.MAX_TARGET_AREA, 1.0)
    
    # Current target proximity
    if current_target:
        last_cx, last_cy, _ = current_target
        target_dist = calculate_distance((cx, cy), (last_cx, last_cy))
        target_score = 1 / (1 + target_dist)
    else:
        target_score = 0
    
    # Combined rating with weights
    return (center_score * Config.CENTER_WEIGHT +
            size_score * Config.SIZE_WEIGHT +
            target_score * Config.CURRENT_TARGET_WEIGHT)

def select_best_target(targets: List[Tuple[int, int, float]],
                      center: Tuple[int, int],
                      current_target: Optional[Tuple[int, int, float]]) -> Optional[Tuple[int, int, float]]:
    """Select best target based on combined rating"""
    if not targets:
        return None
    
    # If current target is still visible, keep it
    if current_target in targets:
        return current_target
    
    # Calculate rating for all targets
    scored_targets = [
        (calculate_target_score(t, center, current_target), t)
        for t in targets
    ]
    
    # Select target with maximum rating
    return max(scored_targets, key=lambda x: x[0])[1]

class TargetDetector:
    """Handles target detection and tracking in the game screen.
    
    This class is responsible for:
    - Detecting potential targets in the game screen
    - Filtering false positives
    - Tracking target movement
    - Calculating target priorities
    """

    def __init__(self, config: dict) -> None:
        """Initialize the target detector.
        
        Args:
            config: Configuration dictionary containing detection parameters
        """
        self.confidence_threshold = config['target_detection']['confidence_threshold']
        self.min_target_size = config['target_detection']['min_target_size']
        self.max_target_distance = config['target_detection']['max_target_distance']
        self.detection_frequency = config['target_detection']['detection_frequency']
        
        # Initialize tracking variables
        self.previous_targets: List[Target] = []
        self.frame_count = 0

    def detect_targets(self, frame: Frame) -> List[Target]:
        """Detect targets in the given frame.
        
        Args:
            frame: Input frame as numpy array
            
        Returns:
            List of detected targets with their properties
        """
        self.frame_count += 1
        if self.frame_count % self.detection_frequency != 0:
            return self.previous_targets

        # Convert frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply threshold
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Process contours
        targets = self._process_contours(contours)
        
        # Update tracking
        self.previous_targets = targets
        return targets

    def _process_contours(self, contours: List[np.ndarray]) -> List[Target]:
        """Process detected contours into target objects.
        
        Args:
            contours: List of detected contours
            
        Returns:
            List of processed targets
        """
        targets: List[Target] = []
        
        for contour in contours:
            # Calculate contour properties
            area = cv2.contourArea(contour)
            if area < self.min_target_size:
                continue
                
            # Get center point
            M = cv2.moments(contour)
            if M["m00"] == 0:
                continue
                
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            
            # Calculate confidence based on contour properties
            confidence = self._calculate_confidence(contour, area)
            if confidence < self.confidence_threshold:
                continue
                
            # Create target object
            target: Target = {
                'position': (cx, cy),
                'size': int(area),
                'confidence': confidence,
                'velocity': self._calculate_velocity((cx, cy)),
                'class_id': 0  # Default class
            }
            
            targets.append(target)
            
        return self._filter_targets(targets)

    def _calculate_confidence(self, contour: np.ndarray, area: float) -> float:
        """Calculate confidence score for a detected contour.
        
        Args:
            contour: Detected contour
            area: Contour area
            
        Returns:
            Confidence score between 0 and 1
        """
        # Calculate shape properties
        perimeter = cv2.arcLength(contour, True)
        circularity = 4 * np.pi * area / (perimeter * perimeter)
        
        # Calculate confidence based on shape properties
        confidence = min(1.0, circularity * (area / self.min_target_size))
        return confidence

    def _calculate_velocity(self, position: Point) -> Optional[Vector]:
        """Calculate target velocity based on previous positions.
        
        Args:
            position: Current target position
            
        Returns:
            Velocity vector or None if not enough data
        """
        if not self.previous_targets:
            return None
            
        # Find closest previous target
        closest_target = min(
            self.previous_targets,
            key=lambda t: np.sqrt(
                (t['position'][0] - position[0])**2 +
                (t['position'][1] - position[1])**2
            )
        )
        
        # Calculate velocity
        dx = position[0] - closest_target['position'][0]
        dy = position[1] - closest_target['position'][1]
        
        return (dx, dy)

    def _filter_targets(self, targets: List[Target]) -> List[Target]:
        """Filter detected targets based on various criteria.
        
        Args:
            targets: List of detected targets
            
        Returns:
            Filtered list of targets
        """
        filtered_targets: List[Target] = []
        
        for target in targets:
            # Check distance from screen center
            center_x, center_y = target['position']
            distance = np.sqrt(center_x**2 + center_y**2)
            
            if distance > self.max_target_distance:
                continue
                
            # Check if target is too close to others
            if self._is_too_close(target, filtered_targets):
                continue
                
            filtered_targets.append(target)
            
        return filtered_targets

    def _is_too_close(self, target: Target, existing_targets: List[Target], min_distance: int = 50) -> bool:
        """Check if a target is too close to existing targets.
        
        Args:
            target: Target to check
            existing_targets: List of existing targets
            min_distance: Minimum allowed distance between targets
            
        Returns:
            True if target is too close to any existing target
        """
        for existing in existing_targets:
            dx = target['position'][0] - existing['position'][0]
            dy = target['position'][1] - existing['position'][1]
            distance = np.sqrt(dx**2 + dy**2)
            
            if distance < min_distance:
                return True
                
        return False 