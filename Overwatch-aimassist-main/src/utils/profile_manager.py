"""
Profile management functions for Overwatch Aim Assist
"""

import os
import json
import logging
from typing import List
from src.core.config import Config

def save_profile(profile_name: str) -> bool:
    """Save current settings to profile"""
    try:
        if not profile_name or '/' in profile_name or '\\' in profile_name:
            raise ValueError("Invalid profile name")
            
        if not os.path.exists(Config.PROFILES_DIR):
            os.makedirs(Config.PROFILES_DIR)
            
        profile_path = os.path.join(Config.PROFILES_DIR, f"{profile_name}.json")
        with open(profile_path, 'w') as f:
            json.dump(Config.to_dict(), f, indent=4)
            
        logging.info(f"Profile {profile_name} saved")
        return True
    except Exception as e:
        logging.error(f"Error saving profile: {str(e)}")
        raise

def load_profile(profile_name: str) -> bool:
    """Load settings from profile"""
    try:
        profile_path = os.path.join(Config.PROFILES_DIR, f"{profile_name}.json")
        if not os.path.exists(profile_path):
            logging.error(f"Profile {profile_name} not found")
            return False
            
        with open(profile_path, 'r') as f:
            data = json.load(f)
            
        Config.from_dict(data)
        logging.info(f"Profile {profile_name} loaded")
        return True
    except Exception as e:
        logging.error(f"Error loading profile: {str(e)}")
        return False

def list_profiles() -> List[str]:
    """Return list of available profiles"""
    if not os.path.exists(Config.PROFILES_DIR):
        return []
        
    profiles = []
    for file in os.listdir(Config.PROFILES_DIR):
        if file.endswith('.json'):
            profiles.append(file[:-5])
    return profiles 