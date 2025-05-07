"""
Integration tests for Overwatch Aim Assist
"""

import pytest
import time
from unittest.mock import patch, MagicMock
import numpy as np
from src.core.aim_state import AimState
from src.core.target_detection import (
    create_target_mask,
    extract_targets,
    select_best_target
)
from src.control.aim_control import (
    calculate_target_velocity,
    predict_target_position,
    move_crosshair
)
from src.utils.profile_manager import save_profile, load_profile
from tests.test_utils import create_test_frame, simulate_target_movement
from src.core.config import Config

@pytest.fixture
def aim_state():
    return AimState()

@pytest.fixture
def test_profile_settings():
    return {
        "BASE_SMOOTHING": 0.5,
        "PREDICTION_ENABLED": True,
        "MAX_PREDICTION_DISTANCE": 100,
        "ACTIVATION_KEY": 0x12  # ALT key
    }

@pytest.mark.integration
@patch('win32api.mouse_event')
def test_full_aiming_cycle(mock_mouse_event, aim_state, test_profile_settings):
    """Test complete aiming cycle with target movement"""
    # Create test profile
    profile_name = "test_profile"
    save_profile(profile_name)
    load_profile(profile_name)
    
    # Simulate target movement
    start_pos = (100, 100)
    velocity = (50, 30)  # pixels per second
    duration = 1.0  # second
    fps = 60
    
    positions = simulate_target_movement(start_pos, velocity, duration, fps)
    
    # Process each frame
    for i, (x, y, size) in enumerate(positions):
        # Create frame with target
        frame = create_test_frame([(x, y, size)])
        
        # Detect targets
        mask = create_target_mask(frame)
        targets = extract_targets(mask)
        current_target = select_best_target(targets, aim_state.screen_center, 
                                         aim_state.current_target)
        
        if current_target:
            # Update aim state
            if aim_state.current_target:
                dt = time.time() - aim_state.last_update_time
                aim_state.target_velocity = calculate_target_velocity(
                    (current_target[0], current_target[1]),
                    aim_state.last_target_pos,
                    dt
                )
            
            aim_state.current_target = current_target
            aim_state.last_target_pos = (current_target[0], current_target[1])
            aim_state.last_update_time = time.time()
            
            # Predict target position
            predicted = predict_target_position(
                (current_target[0], current_target[1]),
                aim_state.target_velocity,
                0.1  # prediction time
            )
            
            # Calculate offset from center
            x_offset = predicted[0] - aim_state.screen_center[0]
            y_offset = predicted[1] - aim_state.screen_center[1]
            
            # Move crosshair
            move_crosshair(x_offset, y_offset, current_target[2], aim_state)
            
            # Verify mouse movement
            if i > 0:  # Skip first frame
                mock_mouse_event.assert_called()

@pytest.mark.integration
def test_error_handling(aim_state):
    """Test system behavior with invalid inputs"""
    # Test with empty frame
    frame = np.zeros((Config.DETECTION_SIZE, Config.DETECTION_SIZE, 3), dtype=np.uint8)
    mask = create_target_mask(frame)
    targets = extract_targets(mask)
    
    # Should handle empty target list
    current_target = select_best_target(targets, aim_state.screen_center, None)
    assert current_target is None
    
    # Test with invalid target positions
    invalid_targets = [(-100, -100, 50), (1000, 1000, 50)]
    frame = create_test_frame(invalid_targets)
    mask = create_target_mask(frame)
    targets = extract_targets(mask)
    
    # Should handle invalid targets
    current_target = select_best_target(targets, aim_state.screen_center, None)
    assert current_target is None

@pytest.mark.slow
def test_performance(aim_state):
    """Test system performance"""
    # Create complex scene with multiple targets
    targets = [
        (100, 100, 50),
        (200, 200, 30),
        (300, 300, 40),
        (400, 400, 60)
    ]
    
    start_time = time.time()
    
    # Process multiple frames
    for _ in range(100):
        frame = create_test_frame(targets)
        mask = create_target_mask(frame)
        targets = extract_targets(mask)
        current_target = select_best_target(targets, aim_state.screen_center, None)
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    # Should process frames quickly enough
    assert processing_time < 1.0  # Less than 1 second for 100 frames

@pytest.mark.parametrize("target_count", [1, 2, 4, 8])
def test_multiple_targets(aim_state, target_count):
    """Test system behavior with different numbers of targets"""
    # Create targets in a circle around center
    targets = []
    for i in range(target_count):
        angle = 2 * np.pi * i / target_count
        x = int(Config.DETECTION_SIZE/2 + 100 * np.cos(angle))
        y = int(Config.DETECTION_SIZE/2 + 100 * np.sin(angle))
        targets.append((x, y, 1000))  # Use larger target size
    
    frame = create_test_frame(targets)
    mask = create_target_mask(frame)
    detected_targets = extract_targets(mask)
    current_target = select_best_target(detected_targets, aim_state.screen_center, None)
    
    assert current_target is not None
    assert len(detected_targets) == target_count 