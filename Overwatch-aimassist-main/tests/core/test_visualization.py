import unittest
import numpy as np
from src.core.visualization import GameVisualizer
from src.core.target_detection import Target

class TestGameVisualizer(unittest.TestCase):
    def setUp(self):
        self.visualizer = GameVisualizer()
        self.test_target = Target(
            position=(10, 10, 0),
            size=(20, 20, 20),
            type="enemy",
            confidence=0.95,
            velocity=(1, 0, 0),
            health=0.75
        )
    
    def test_initialization(self):
        """Test visualizer initialization"""
        self.assertEqual(self.visualizer.window_name, "Overwatch Vision")
        self.assertEqual(self.visualizer.window_size, (800, 600))
        self.assertFalse(self.visualizer.is_running)
        self.assertIn("enemy", self.visualizer.colors)
        self.assertIn("thermal", self.visualizer.vision_effects)
    
    def test_window_management(self):
        """Test window creation and closing"""
        self.visualizer.create_window()
        self.assertTrue(self.visualizer.is_running)
        
        self.visualizer.close_window()
        self.assertFalse(self.visualizer.is_running)
    
    def test_draw_targets(self):
        """Test target drawing functionality"""
        targets = [self.test_target]
        frame = self.visualizer.draw_targets(targets)
        
        # Check frame properties
        self.assertEqual(frame.shape, (600, 800, 3))
        self.assertEqual(frame.dtype, np.uint8)
    
    def test_draw_world(self):
        """Test world drawing functionality"""
        frame = self.visualizer.draw_world()
        
        # Check frame properties
        self.assertEqual(frame.shape, (600, 800, 3))
        self.assertEqual(frame.dtype, np.uint8)
    
    def test_draw_primitive(self):
        """Test primitive shape drawing"""
        # Test cube
        cube_frame = self.visualizer.draw_primitive(
            "cube", (0, 0, 0), (20, 20, 20)
        )
        self.assertEqual(cube_frame.shape, (600, 800, 3))
        
        # Test sphere
        sphere_frame = self.visualizer.draw_primitive(
            "sphere", (0, 0, 0), 20
        )
        self.assertEqual(sphere_frame.shape, (600, 800, 3))
        
        # Test cylinder
        cylinder_frame = self.visualizer.draw_primitive(
            "cylinder", (0, 0, 0), (20, 40)
        )
        self.assertEqual(cylinder_frame.shape, (600, 800, 3))
    
    def test_vision_effects(self):
        """Test vision effect application"""
        # Create test frame
        test_frame = np.zeros((100, 100, 3), dtype=np.uint8)
        
        # Test thermal effect
        thermal_frame = self.visualizer.apply_vision_effect(test_frame, "thermal")
        self.assertEqual(thermal_frame.shape, (100, 100, 3))
        
        # Test night vision
        night_vision_frame = self.visualizer.apply_vision_effect(test_frame, "night_vision")
        self.assertEqual(night_vision_frame.shape, (100, 100, 3))
        
        # Test outline
        outline_frame = self.visualizer.apply_vision_effect(test_frame, "outline")
        self.assertEqual(outline_frame.shape, (100, 100, 3))
    
    def test_depth_visualization(self):
        """Test depth map visualization"""
        # Create test depth map
        depth_map = np.random.rand(100, 100)
        
        # Visualize depth
        depth_vis = self.visualizer.visualize_depth(depth_map)
        self.assertEqual(depth_vis.shape, (100, 100, 3))
    
    def test_target_info_drawing(self):
        """Test target information drawing"""
        frame = np.zeros((600, 800, 3), dtype=np.uint8)
        
        # Draw target info
        self.visualizer._draw_target_info(frame, self.test_target)
        
        # Check frame properties
        self.assertEqual(frame.shape, (600, 800, 3))
        self.assertEqual(frame.dtype, np.uint8)
    
    def test_3d_projection(self):
        """Test 3D to 2D projection"""
        # Test single point projection
        point_3d = (10, 20, 30)
        point_2d = self.visualizer._project_point(point_3d)
        self.assertEqual(len(point_2d), 2)
        
        # Test multiple points projection
        points_3d = [(10, 20, 30), (40, 50, 60)]
        points_2d = self.visualizer._project_points(points_3d)
        self.assertEqual(len(points_2d), 2)
        self.assertEqual(len(points_2d[0]), 2)

if __name__ == '__main__':
    unittest.main() 