"""
Tests for target detection module
"""

import pytest
import numpy as np
from src.core.target_detection import (
    calculate_distance,
    create_target_mask,
    extract_targets,
    calculate_target_score,
    select_best_target
)
from src.core.config import Config
from tests.test_utils import create_test_frame

@pytest.fixture
def center():
    return (Config.DETECTION_SIZE // 2, Config.DETECTION_SIZE // 2)

def test_calculate_distance():
    """Test distance calculation between points"""
    p1 = (0, 0)
    p2 = (3, 4)
    assert calculate_distance(p1, p2) == 5.0

def test_create_target_mask():
    """Test target mask creation"""
    frame = create_test_frame([(100, 100, 50)])
    mask = create_target_mask(frame)
    assert np.any(mask > 0)

def test_extract_targets():
    """Test target extraction from mask"""
    targets = [(50, 50, 1000), (150, 150, 800), (250, 250, 600)]  # Targets further apart
    frame = create_test_frame(targets)
    mask = create_target_mask(frame)
    extracted = extract_targets(mask)
    
    # Check number of targets
    assert len(extracted) == len(targets)
    
    # Sort both lists by area in descending order
    targets.sort(key=lambda x: x[2], reverse=True)
    extracted.sort(key=lambda x: x[2], reverse=True)
    
    # Verify target properties
    for i, (target, extracted_target) in enumerate(zip(targets, extracted)):
        # Check position (allow more error for larger targets)
        max_error = int(np.sqrt(target[2]) / 4)  # Allow error proportional to target size
        assert abs(target[0] - extracted_target[0]) <= max_error
        assert abs(target[1] - extracted_target[1]) <= max_error
        
        # Check relative sizes (each target should be smaller than the previous one)
        if i > 0:
            assert extracted_target[2] < extracted[i-1][2]

def test_calculate_target_score(center):
    """Test target scoring"""
    target = (100, 100, 1000)
    current_target = (150, 150, 800)
    score = calculate_target_score(target, center, current_target)
    assert 0 < score < 3.0

def test_select_best_target(center):
    """Test best target selection"""
    targets = [
        (100, 100, 1000),  # Close to center
        (400, 400, 2000),  # Far from center but large
        (150, 150, 800)    # Close to current target
    ]
    current_target = (160, 160, 800)
    best = select_best_target(targets, center, current_target)
    assert best in targets

@pytest.mark.slow
def test_target_tracking(center):
    """Test target tracking over multiple frames"""
    positions = []
    current_target = None
    
    for x, y, size in [(100, 100, 1000), (150, 130, 1000), (200, 160, 1000)]:
        frame = create_test_frame([(x, y, size)])
        mask = create_target_mask(frame)
        targets = extract_targets(mask)
        current_target = select_best_target(targets, center, current_target)
        positions.append(current_target)
    
    assert len(positions) == 3
    assert positions[-1] is not None

@pytest.mark.parametrize("target_pos,expected_detected", [
    ((100, 100, 1000), True),
    ((0, 0, 1000), True),
    ((Config.DETECTION_SIZE-1, Config.DETECTION_SIZE-1, 1000), True),
    ((-100, -100, 1000), False),
    ((Config.DETECTION_SIZE+100, Config.DETECTION_SIZE+100, 1000), False),
])
def test_target_detection_boundaries(target_pos, expected_detected):
    """Test target detection at different positions"""
    frame = create_test_frame([target_pos])
    mask = create_target_mask(frame)
    targets = extract_targets(mask)
    assert (len(targets) > 0) == expected_detected 