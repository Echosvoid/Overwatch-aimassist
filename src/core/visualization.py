import cv2
import numpy as np
import math
from typing import List, Tuple, Optional, Dict, Any
from .target_detection import Target

class GameVisualizer:
    """Visualizes game world and targets using primitive shapes"""
    
    def __init__(self):
        self.window_name = "Overwatch Vision"
        self.window_size = (800, 600)
        self.is_running = False
        self.colors = {
            "enemy": (0, 0, 255),  # Red
            "ally": (0, 255, 0),   # Green
            "neutral": (255, 255, 0)  # Yellow
        }
        self.vision_effects = {
            "thermal": self._apply_thermal_effect,
            "night_vision": self._apply_night_vision,
            "outline": self._apply_outline
        }
    
    def create_window(self) -> None:
        """Create visualization window"""
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, *self.window_size)
        self.is_running = True
    
    def close_window(self) -> None:
        """Close visualization window"""
        cv2.destroyWindow(self.window_name)
        self.is_running = False
    
    def draw_targets(self, targets: List[Target]) -> np.ndarray:
        """Draw detected targets"""
        frame = np.zeros((self.window_size[1], self.window_size[0], 3), dtype=np.uint8)
        
        for target in targets:
            # Draw target as a cube
            self._draw_cube(frame, target.position, target.size, self.colors.get(target.type, (255, 255, 255)))
            
            # Draw target info
            self._draw_target_info(frame, target)
        
        return frame
    
    def draw_world(self) -> np.ndarray:
        """Draw game world representation"""
        frame = np.zeros((self.window_size[1], self.window_size[0], 3), dtype=np.uint8)
        
        # Draw ground plane
        self._draw_ground_plane(frame)
        
        # Draw coordinate system
        self._draw_coordinate_system(frame)
        
        return frame
    
    def add_vision_overlay(self, base_frame: np.ndarray, targets: List[Target]) -> np.ndarray:
        """Add vision overlay to base frame"""
        overlay = np.zeros_like(base_frame)
        
        # Draw targets with vision effects
        for target in targets:
            if target.is_visible((0, 0, 0), (0, 0, 1)):  # Simple visibility check
                self._draw_target_with_vision(overlay, target)
        
        # Blend overlay with base frame
        alpha = 0.7
        return cv2.addWeighted(base_frame, 1 - alpha, overlay, alpha, 0)
    
    def draw_primitive(self, obj_type: str, position: Tuple[float, float, float], size: Any) -> np.ndarray:
        """Draw primitive object"""
        frame = np.zeros((self.window_size[1], self.window_size[0], 3), dtype=np.uint8)
        
        if obj_type == "cube":
            self._draw_cube(frame, position, size, (255, 255, 255))
        elif obj_type == "sphere":
            self._draw_sphere(frame, position, size, (255, 255, 255))
        elif obj_type == "cylinder":
            self._draw_cylinder(frame, position, size, (255, 255, 255))
        
        return frame
    
    def visualize_depth(self, depth_map: np.ndarray) -> np.ndarray:
        """Visualize depth map"""
        # Normalize depth map to 0-255
        depth_normalized = cv2.normalize(depth_map, None, 0, 255, cv2.NORM_MINMAX)
        depth_colored = cv2.applyColorMap(depth_normalized.astype(np.uint8), cv2.COLORMAP_JET)
        return depth_colored
    
    def apply_vision_effect(self, frame: np.ndarray, effect: str) -> np.ndarray:
        """Apply vision effect to frame"""
        if effect in self.vision_effects:
            return self.vision_effects[effect](frame)
        return frame
    
    def _draw_cube(self, frame: np.ndarray, position: Tuple[float, float, float], 
                  size: Tuple[float, float, float], color: Tuple[int, int, int]) -> None:
        """Draw 3D cube"""
        # Project 3D points to 2D
        points_3d = self._get_cube_points(position, size)
        points_2d = self._project_points(points_3d)
        
        # Draw cube edges
        edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),  # Bottom face
            (4, 5), (5, 6), (6, 7), (7, 4),  # Top face
            (0, 4), (1, 5), (2, 6), (3, 7)   # Connecting edges
        ]
        
        for edge in edges:
            pt1 = tuple(map(int, points_2d[edge[0]]))
            pt2 = tuple(map(int, points_2d[edge[1]]))
            cv2.line(frame, pt1, pt2, color, 2)
    
    def _draw_sphere(self, frame: np.ndarray, position: Tuple[float, float, float], 
                    radius: float, color: Tuple[int, int, int]) -> None:
        """Draw sphere"""
        # Project center to 2D
        center_2d = self._project_point(position)
        
        # Draw circle
        cv2.circle(frame, tuple(map(int, center_2d)), int(radius), color, 2)
    
    def _draw_cylinder(self, frame: np.ndarray, position: Tuple[float, float, float], 
                      size: Tuple[float, float], color: Tuple[int, int, int]) -> None:
        """Draw cylinder"""
        radius, height = size
        
        # Draw top and bottom circles
        top_center = self._project_point((position[0], position[1], position[2] + height))
        bottom_center = self._project_point(position)
        
        cv2.circle(frame, tuple(map(int, top_center)), int(radius), color, 2)
        cv2.circle(frame, tuple(map(int, bottom_center)), int(radius), color, 2)
        
        # Draw connecting lines
        cv2.line(frame, 
                tuple(map(int, (top_center[0] + radius, top_center[1]))),
                tuple(map(int, (bottom_center[0] + radius, bottom_center[1]))),
                color, 2)
        cv2.line(frame,
                tuple(map(int, (top_center[0] - radius, top_center[1]))),
                tuple(map(int, (bottom_center[0] - radius, bottom_center[1]))),
                color, 2)
    
    def _draw_ground_plane(self, frame: np.ndarray) -> None:
        """Draw ground plane"""
        # Draw grid
        grid_size = 100
        grid_spacing = 20
        
        for i in range(-grid_size, grid_size + 1, grid_spacing):
            # Draw horizontal lines
            pt1 = self._project_point((i, -grid_size, 0))
            pt2 = self._project_point((i, grid_size, 0))
            cv2.line(frame, tuple(map(int, pt1)), tuple(map(int, pt2)), (50, 50, 50), 1)
            
            # Draw vertical lines
            pt1 = self._project_point((-grid_size, i, 0))
            pt2 = self._project_point((grid_size, i, 0))
            cv2.line(frame, tuple(map(int, pt1)), tuple(map(int, pt2)), (50, 50, 50), 1)
    
    def _draw_coordinate_system(self, frame: np.ndarray) -> None:
        """Draw coordinate system"""
        origin = self._project_point((0, 0, 0))
        
        # Draw axes
        x_axis = self._project_point((100, 0, 0))
        y_axis = self._project_point((0, 100, 0))
        z_axis = self._project_point((0, 0, 100))
        
        cv2.line(frame, tuple(map(int, origin)), tuple(map(int, x_axis)), (0, 0, 255), 2)  # X - Red
        cv2.line(frame, tuple(map(int, origin)), tuple(map(int, y_axis)), (0, 255, 0), 2)  # Y - Green
        cv2.line(frame, tuple(map(int, origin)), tuple(map(int, z_axis)), (255, 0, 0), 2)  # Z - Blue
    
    def _draw_target_info(self, frame: np.ndarray, target: Target) -> None:
        """Draw target information"""
        center = self._project_point(target.get_center())
        
        # Draw health bar if available
        if target.health is not None:
            health_width = 50
            health_height = 5
            health_x = int(center[0] - health_width / 2)
            health_y = int(center[1] - 30)
            
            # Background
            cv2.rectangle(frame, (health_x, health_y), 
                         (health_x + health_width, health_y + health_height), 
                         (50, 50, 50), -1)
            
            # Health
            health_amount = int(health_width * target.health)
            cv2.rectangle(frame, (health_x, health_y), 
                         (health_x + health_amount, health_y + health_height), 
                         (0, 255, 0), -1)
    
    def _draw_target_with_vision(self, frame: np.ndarray, target: Target) -> None:
        """Draw target with vision effects"""
        # Draw target outline
        center = self._project_point(target.get_center())
        radius = int(target.size[0] / 2)
        
        # Draw thermal effect
        if target.type == "enemy":
            cv2.circle(frame, tuple(map(int, center)), radius, (0, 0, 255), 2)
        else:
            cv2.circle(frame, tuple(map(int, center)), radius, (0, 255, 0), 2)
    
    def _get_cube_points(self, position: Tuple[float, float, float], 
                        size: Tuple[float, float, float]) -> List[Tuple[float, float, float]]:
        """Get cube vertices"""
        x, y, z = position
        w, h, d = size
        
        return [
            (x, y, z), (x + w, y, z), (x + w, y + h, z), (x, y + h, z),  # Bottom face
            (x, y, z + d), (x + w, y, z + d), (x + w, y + h, z + d), (x, y + h, z + d)  # Top face
        ]
    
    def _project_points(self, points_3d: List[Tuple[float, float, float]]) -> List[Tuple[float, float]]:
        """Project 3D points to 2D"""
        return [self._project_point(p) for p in points_3d]
    
    def _project_point(self, point_3d: Tuple[float, float, float]) -> Tuple[float, float]:
        """Project single 3D point to 2D"""
        # Simple orthographic projection
        x, y, z = point_3d
        scale = 2.0
        
        # Center the projection
        center_x = self.window_size[0] / 2
        center_y = self.window_size[1] / 2
        
        # Project to 2D
        x_2d = center_x + x * scale
        y_2d = center_y - y * scale  # Flip Y axis
        
        return (x_2d, y_2d)
    
    def _apply_thermal_effect(self, frame: np.ndarray) -> np.ndarray:
        """Apply thermal vision effect"""
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply colormap
        thermal = cv2.applyColorMap(gray, cv2.COLORMAP_JET)
        
        return thermal
    
    def _apply_night_vision(self, frame: np.ndarray) -> np.ndarray:
        """Apply night vision effect"""
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply green tint
        night_vision = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        night_vision[:, :, 0] = 0  # Remove blue
        night_vision[:, :, 2] = 0  # Remove red
        
        return night_vision
    
    def _apply_outline(self, frame: np.ndarray) -> np.ndarray:
        """Apply outline effect"""
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply edge detection
        edges = cv2.Canny(gray, 100, 200)
        
        # Convert back to BGR
        outline = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        
        return outline 