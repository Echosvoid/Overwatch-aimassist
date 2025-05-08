"""
Overwatch Advanced Aim Assist

Enhanced aiming assistance system for Overwatch with:
- Intelligent target selection among multiple enemies
- Smooth and natural crosshair movement
- Priority system (size, position, current target)
- Customizable parameters
"""

import cv2
import numpy as np
import mss
import pyautogui
import time
import logging
import os
from src.core.config import Config
from src.core.aim_state import AimState
from src.core.target_detection import create_target_mask, extract_targets, select_best_target
from src.control.aim_control import is_activated, calculate_target_velocity, predict_target_position, move_crosshair
from src.utils.profile_manager import save_profile, load_profile, list_profiles
from src.utils.results_manager import ResultsManager

# Initialize results manager
results_manager = ResultsManager()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='logs/aim_assist.log'
)

# Initialize aim state
aim_state = AimState()

def main_loop():
    """Main processing loop"""
    logging.info("Overwatch Aim Assist started")
    print("Overwatch Aim Assist started")
    print(f"Hold ALT to activate | Offset: {Config.VERTICAL_OFFSET}px")
    print("D - toggle debug mode | Q - exit")
    print("S - save profile | L - load profile")
    
    # Load default profile on startup
    if os.path.exists(os.path.join(Config.PROFILES_DIR, Config.DEFAULT_PROFILE)):
        load_profile(Config.DEFAULT_PROFILE)
    
    frame_time = 1.0 / Config.FPS_LIMIT
    last_frame_time = time.time()
    
    try:
        with mss.mss() as sct:
            monitor = {
                "top": 0,
                "left": 0,
                "width": Config.DETECTION_SIZE,
                "height": Config.DETECTION_SIZE
            }
            
            while True:
                try:
                    # FPS limiting
                    current_time = time.time()
                    elapsed = current_time - last_frame_time
                    if elapsed < frame_time:
                        time.sleep(frame_time - elapsed)
                    last_frame_time = time.time()
                    
                    # Center detection area around cursor
                    mouse_x, mouse_y = pyautogui.position()
                    monitor['left'] = max(0, mouse_x - Config.DETECTION_SIZE // 2)
                    monitor['top'] = max(0, mouse_y - Config.DETECTION_SIZE // 2)
                    
                    # Screen capture
                    frame = np.array(sct.grab(monitor))
                    
                    # Frame processing
                    mask = create_target_mask(frame)
                    targets = extract_targets(mask)
                    
                    # Log target detections
                    if targets:
                        for target in targets:
                            cx, cy, area = target
                            results_manager.log_target_detection({
                                "timestamp": current_time,
                                "position": {"x": cx, "y": cy},
                                "area": area,
                                "mouse_position": {"x": mouse_x, "y": mouse_y}
                            })
                    
                    # Target selection
                    current_target = (
                        aim_state.current_target 
                        if time.time() - aim_state.last_target_time < Config.TARGET_LOCK_TIME 
                        else None
                    )
                    
                    best_target = select_best_target(targets, aim_state.screen_center, current_target)
                    
                    # Crosshair update
                    if best_target and is_activated():
                        cx, cy, area = best_target
                        
                        # Update target velocity
                        if aim_state.last_target_pos != (0, 0):
                            aim_state.target_velocity = calculate_target_velocity(
                                (cx, cy),
                                aim_state.last_target_pos,
                                current_time - aim_state.last_update_time
                            )
                        
                        # Predict target position
                        predicted_pos = predict_target_position(
                            (cx, cy),
                            aim_state.target_velocity,
                            Config.PREDICTION_TIME
                        )
                        
                        # Log prediction
                        results_manager.log_prediction({
                            "timestamp": current_time,
                            "current_position": {"x": cx, "y": cy},
                            "predicted_position": {"x": predicted_pos[0], "y": predicted_pos[1]},
                            "velocity": {"x": aim_state.target_velocity[0], "y": aim_state.target_velocity[1]}
                        })
                        
                        aim_state.last_target_pos = (cx, cy)
                        aim_state.last_target_time = current_time
                        aim_state.current_target = best_target
                        
                        x_offset = predicted_pos[0] - aim_state.screen_center[0]
                        y_offset = (predicted_pos[1] - aim_state.screen_center[1]) + Config.VERTICAL_OFFSET
                        
                        # Log shot attempt
                        results_manager.log_shot({
                            "timestamp": current_time,
                            "target_position": {"x": cx, "y": cy},
                            "crosshair_offset": {"x": x_offset, "y": y_offset},
                            "target_area": area
                        })
                        
                        move_crosshair(x_offset, y_offset, area, aim_state)
                        
                        # Save screenshot of the shot
                        _, buffer = cv2.imencode('.png', frame)
                        results_manager.save_screenshot(
                            buffer.tobytes(),
                            {
                                "timestamp": current_time,
                                "target_position": {"x": cx, "y": cy},
                                "crosshair_position": {"x": mouse_x, "y": mouse_y},
                                "target_area": area
                            }
                        )
                    
                    # Debug visualization
                    if Config.DEBUG_MODE:
                        debug_img = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
                        
                        # Draw center
                        cv2.circle(debug_img, aim_state.screen_center, 3, (0, 255, 0), -1)
                        
                        # Draw all targets
                        for target in targets:
                            cx, cy, _ = target
                            cv2.circle(debug_img, (cx, cy), 3, (0, 0, 255), -1)
                        
                        # Draw selected target
                        if best_target:
                            bx, by, _ = best_target
                            cv2.circle(debug_img, (bx, by), 5, (255, 0, 0), 2)
                            cv2.putText(debug_img, "TARGET", (bx+10, by), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                        
                        cv2.imshow("Overwatch Aim Assist [DEBUG]", debug_img)
                    
                    # Key handling
                    key = cv2.waitKey(1) & 0xFF
                    if key == Config.EXIT_KEY:
                        # Save final session summary
                        summary = results_manager.get_session_summary()
                        print("\nSession Summary:")
                        for key, value in summary.items():
                            print(f"{key}: {value}")
                        break
                    elif key == Config.TOGGLE_DEBUG_KEY:
                        Config.DEBUG_MODE = not Config.DEBUG_MODE
                        if not Config.DEBUG_MODE:
                            cv2.destroyAllWindows()
                        logging.info(f"Debug mode {'enabled' if Config.DEBUG_MODE else 'disabled'}")
                    elif key == Config.SAVE_PROFILE_KEY:
                        profile_name = input("Enter profile name to save: ")
                        if save_profile(profile_name):
                            print(f"Profile {profile_name} saved")
                    elif key == Config.LOAD_PROFILE_KEY:
                        profiles = list_profiles()
                        if profiles:
                            print("\nAvailable profiles:")
                            for i, profile in enumerate(profiles, 1):
                                print(f"{i}. {profile}")
                            try:
                                choice = int(input("\nSelect profile number: "))
                                if 1 <= choice <= len(profiles):
                                    if load_profile(profiles[choice-1]):
                                        print(f"Profile {profiles[choice-1]} loaded")
                            except ValueError:
                                print("Invalid input")
                        else:
                            print("No profiles available")
                
                except Exception as e:
                    logging.error(f"Error in main loop: {str(e)}")
                    # Log difficulty
                    results_manager.log_difficulty({
                        "timestamp": time.time(),
                        "error": str(e),
                        "error_type": type(e).__name__
                    })
                    continue
                
    except Exception as e:
        logging.error(f"Critical error: {str(e)}")
    finally:
        cv2.destroyAllWindows()
        logging.info("Overwatch Aim Assist stopped")

if __name__ == "__main__":
    main_loop() 