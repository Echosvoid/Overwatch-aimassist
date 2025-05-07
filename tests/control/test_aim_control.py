"""
Tests for aim control module
"""

import pytest
from unittest.mock import patch, MagicMock
from src.control.aim_control import (
    is_activated,
    calculate_target_velocity,
    predict_target_position,
    adaptive_smoothing,
    move_crosshair
)
from src.core.config import Config
from src.core.aim_state import AimState

@pytest.fixture
def aim_state():
    return AimState()

@pytest.mark.parametrize("key_state,expected", [
    (-1, True),   # Key pressed
    (0, False),   # Key not pressed
])
def test_is_activated(key_state, expected):
    """Test activation key detection"""
    with patch('win32api.GetAsyncKeyState', return_value=key_state):
        assert is_activated() == expected

def test_calculate_target_velocity():
    """Test target velocity calculation"""
    current_pos = (100, 100)
    last_pos = (50, 50)
    dt = 1.0
    
    vx, vy = calculate_target_velocity(current_pos, last_pos, dt)
    assert vx == 50.0
    assert vy == 50.0

@pytest.mark.parametrize("current_pos,velocity,prediction_time,expected", [
    ((100, 100), (50, 30), 0.5, (125, 115)),
    ((0, 0), (70, 70), 1.0, (70, 70)),
    ((200, 200), (-50, -30), 0.5, (175, 185)),
])
def test_predict_target_position(current_pos, velocity, prediction_time, expected):
    """Test target position prediction"""
    predicted = predict_target_position(current_pos, velocity, prediction_time)
    assert predicted == expected

@pytest.mark.parametrize("target_size,distance,velocity", [
    (1000, 200, 500),
    (500, 100, 1000),
    (2000, 400, 250),
])
def test_adaptive_smoothing(target_size, distance, velocity):
    """Test adaptive smoothing calculation"""
    smoothing = adaptive_smoothing(target_size, distance, velocity)
    assert 0.1 <= smoothing <= 1.0

def test_move_crosshair(aim_state):
    """Test crosshair movement"""
    x_offset = 100
    y_offset = 50
    target_size = 1000
    
    with patch('win32api.mouse_event') as mock_mouse_event:
        move_crosshair(x_offset, y_offset, target_size, aim_state)
        mock_mouse_event.assert_called_once()

@pytest.mark.integration
def test_aim_control_integration():
    """Test integration of aim control components"""
    current_pos = (100, 100)
    last_pos = (50, 50)
    dt = 1.0
    
    # Calculate velocity
    velocity = calculate_target_velocity(current_pos, last_pos, dt)
    
    # Predict position
    predicted = predict_target_position(current_pos, velocity, 0.5)
    
    # Calculate smoothing
    distance = ((predicted[0] - current_pos[0])**2 + 
               (predicted[1] - current_pos[1])**2)**0.5
    smoothing = adaptive_smoothing(1000, distance, 
                                 (velocity[0]**2 + velocity[1]**2)**0.5)
    
    # Verify results
    assert isinstance(predicted, tuple)
    assert len(predicted) == 2
    assert 0.1 <= smoothing <= 1.0

@pytest.mark.parametrize("invalid_input", [
    ((None, None), (50, 50), 1.0),
    ((100, 100), (None, None), 1.0),
    ((100, 100), (50, 50), None),
])
def test_calculate_target_velocity_invalid_input(invalid_input):
    """Test target velocity calculation with invalid inputs"""
    with pytest.raises(Exception):
        calculate_target_velocity(*invalid_input) 