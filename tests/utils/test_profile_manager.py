"""
Tests for profile manager module
"""

import pytest
import os
import json
import shutil
from src.utils.profile_manager import save_profile, load_profile, list_profiles
from src.core.config import Config
from tests.test_utils import create_test_profile

@pytest.fixture
def test_profiles_dir(tmp_path):
    """Create temporary profiles directory"""
    Config.PROFILES_DIR = str(tmp_path)
    return tmp_path

@pytest.fixture
def test_profile_settings():
    """Default test profile settings"""
    return {
        "BASE_SMOOTHING": 0.5,
        "PREDICTION_ENABLED": True,
        "MAX_PREDICTION_DISTANCE": 100
    }

def test_save_profile(test_profiles_dir, test_profile_settings):
    """Test profile saving"""
    profile_name = "test_profile"
    success = save_profile(profile_name)
    assert success
    
    profile_path = os.path.join(test_profiles_dir, f"{profile_name}.json")
    assert os.path.exists(profile_path)

def test_load_profile(test_profiles_dir, test_profile_settings):
    """Test profile loading"""
    profile_name = "test_profile"
    create_test_profile(profile_name, test_profile_settings)
    
    success = load_profile(profile_name)
    assert success
    
    assert Config.BASE_SMOOTHING == test_profile_settings["BASE_SMOOTHING"]
    assert Config.PREDICTION_ENABLED == test_profile_settings["PREDICTION_ENABLED"]
    assert Config.MAX_PREDICTION_DISTANCE == test_profile_settings["MAX_PREDICTION_DISTANCE"]

@pytest.mark.parametrize("profile_names", [
    ["profile1"],
    ["profile1", "profile2"],
    ["profile1", "profile2", "profile3"],
])
def test_list_profiles(test_profiles_dir, profile_names):
    """Test profile listing"""
    for name in profile_names:
        create_test_profile(name, {"test": "value"})
    
    found_profiles = list_profiles()
    assert len(found_profiles) == len(profile_names)
    for profile in profile_names:
        assert profile in found_profiles

@pytest.mark.integration
def test_profile_integration(test_profiles_dir, test_profile_settings):
    """Test profile management integration"""
    profile_name = "test_profile"
    
    # Create and save profile
    create_test_profile(profile_name, test_profile_settings)
    
    # List profiles
    profiles = list_profiles()
    assert profile_name in profiles
    
    # Load profile
    success = load_profile(profile_name)
    assert success
    
    # Verify settings
    assert Config.BASE_SMOOTHING == test_profile_settings["BASE_SMOOTHING"]
    assert Config.PREDICTION_ENABLED == test_profile_settings["PREDICTION_ENABLED"]
    assert Config.MAX_PREDICTION_DISTANCE == test_profile_settings["MAX_PREDICTION_DISTANCE"]

@pytest.mark.parametrize("invalid_profile", [
    "nonexistent_profile",
    "",
    "invalid/profile/name",
])
def test_load_nonexistent_profile(test_profiles_dir, invalid_profile):
    """Test loading nonexistent profiles"""
    success = load_profile(invalid_profile)
    assert not success

def test_save_profile_invalid_name(test_profiles_dir):
    """Test saving profile with invalid name"""
    with pytest.raises(Exception):
        save_profile("")

def test_profile_file_corruption(test_profiles_dir):
    """Test handling corrupted profile files"""
    profile_name = "corrupted_profile"
    profile_path = os.path.join(test_profiles_dir, f"{profile_name}.json")
    
    # Create corrupted profile file
    with open(profile_path, 'w') as f:
        f.write("invalid json content")
    
    success = load_profile(profile_name)
    assert not success 