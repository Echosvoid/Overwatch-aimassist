"""
Pytest configuration and common fixtures
"""

import pytest
import os
import sys
from src.core.config import Config

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment before each test"""
    # Save original config values
    original_config = {
        'PROFILES_DIR': Config.PROFILES_DIR,
        'DETECTION_SIZE': Config.DETECTION_SIZE,
        'BASE_SMOOTHING': Config.BASE_SMOOTHING,
        'PREDICTION_ENABLED': Config.PREDICTION_ENABLED,
        'MAX_PREDICTION_DISTANCE': Config.MAX_PREDICTION_DISTANCE
    }
    
    yield
    
    # Restore original config values
    Config.PROFILES_DIR = original_config['PROFILES_DIR']
    Config.DETECTION_SIZE = original_config['DETECTION_SIZE']
    Config.BASE_SMOOTHING = original_config['BASE_SMOOTHING']
    Config.PREDICTION_ENABLED = original_config['PREDICTION_ENABLED']
    Config.MAX_PREDICTION_DISTANCE = original_config['MAX_PREDICTION_DISTANCE']

@pytest.fixture
def mock_win32api():
    """Mock win32api functions"""
    with pytest.MonkeyPatch.context() as m:
        m.setattr('win32api.GetAsyncKeyState', lambda x: 0)
        m.setattr('win32api.mouse_event', lambda *args: None)
        yield m 