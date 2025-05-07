# Overwatch Aim Assist Documentation

## Table of Contents
1. [Introduction](#introduction)
2. [System Architecture](#system-architecture)
3. [Core Components](#core-components)
4. [Configuration Guide](#configuration-guide)
5. [API Reference](#api-reference)
6. [Troubleshooting](#troubleshooting)
7. [Performance Optimization](#performance-optimization)

## Introduction

Overwatch Aim Assist is a sophisticated computer vision-based aiming assistant that enhances gaming performance in Overwatch. This documentation provides detailed information about the system's architecture, components, and usage.

### Key Features
- Real-time target detection and tracking
- Intelligent aim assistance
- Customizable settings
- Profile management
- Performance optimization

## System Architecture

### Overview
The system consists of several interconnected modules:
1. Target Detection Module
2. Aim Control Module
3. Configuration Manager
4. Profile Manager
5. User Interface

### Data Flow
```
[Game Screen] → [Target Detection] → [Aim Control] → [Mouse Movement]
     ↑              ↓                    ↓
[Configuration] ← [Profile Manager] ← [User Input]
```

## Core Components

### 1. Target Detection Module
Located in `src/core/target_detection.py`

#### Key Functions:
- `detect_targets()`: Identifies potential targets in the game screen
- `filter_targets()`: Applies filters to remove false positives
- `calculate_target_priority()`: Determines target priority based on various factors

#### Usage Example:
```python
from src.core.target_detection import TargetDetector

detector = TargetDetector()
targets = detector.detect_targets(screen_capture)
```

### 2. Aim Control Module
Located in `src/control/aim_control.py`

#### Key Functions:
- `calculate_aim_vector()`: Computes optimal aim direction
- `apply_smoothing()`: Implements aim smoothing
- `predict_target_position()`: Predicts target movement

#### Usage Example:
```python
from src.control.aim_control import AimController

controller = AimController()
aim_vector = controller.calculate_aim_vector(current_pos, target_pos)
```

### 3. Configuration Manager
Located in `src/utils/config_manager.py`

#### Key Functions:
- `load_config()`: Loads configuration from file
- `save_config()`: Saves current configuration
- `validate_config()`: Validates configuration parameters

#### Configuration Parameters:
```json
{
    "sensitivity": {
        "type": "float",
        "range": [0.1, 2.0],
        "default": 1.0
    },
    "smoothing": {
        "type": "float",
        "range": [0.0, 1.0],
        "default": 0.5
    },
    "prediction": {
        "type": "boolean",
        "default": true
    }
}
```

## Configuration Guide

### Basic Configuration
1. Edit `config.json` in the project root
2. Adjust parameters within recommended ranges
3. Save and restart the application

### Advanced Configuration
1. Sensitivity Settings
   - Base sensitivity: 1.0
   - ADS multiplier: 0.8
   - Scope sensitivity: 0.5

2. Target Detection
   - Confidence threshold: 0.7
   - Minimum target size: 20px
   - Maximum target distance: 1000px

3. Aim Assistance
   - Smoothing factor: 0.5
   - Prediction time: 0.1s
   - Max angle correction: 45°

## API Reference

### Target Detection API
```python
class TargetDetector:
    def detect_targets(self, frame: np.ndarray) -> List[Target]:
        """
        Detect targets in the given frame.
        
        Args:
            frame: Input frame as numpy array
            
        Returns:
            List of detected targets
        """
        pass

    def filter_targets(self, targets: List[Target]) -> List[Target]:
        """
        Filter detected targets based on criteria.
        
        Args:
            targets: List of detected targets
            
        Returns:
            Filtered list of targets
        """
        pass
```

### Aim Control API
```python
class AimController:
    def calculate_aim_vector(self, current_pos: Tuple[int, int], 
                           target_pos: Tuple[int, int]) -> Tuple[float, float]:
        """
        Calculate aim vector from current position to target.
        
        Args:
            current_pos: Current aim position
            target_pos: Target position
            
        Returns:
            Aim vector as (x, y) tuple
        """
        pass

    def apply_smoothing(self, vector: Tuple[float, float]) -> Tuple[float, float]:
        """
        Apply smoothing to aim movement.
        
        Args:
            vector: Raw aim vector
            
        Returns:
            Smoothed aim vector
        """
        pass
```

## Troubleshooting

### Common Issues

1. High CPU Usage
   - Solution: Enable GPU acceleration
   - Adjust target detection frequency
   - Reduce processing resolution

2. Detection Issues
   - Check lighting conditions
   - Adjust confidence threshold
   - Update target detection model

3. Aim Assistance Problems
   - Calibrate sensitivity
   - Adjust smoothing factor
   - Check prediction settings

### Debug Mode
Enable debug mode by setting `debug: true` in config.json to access:
- Real-time detection visualization
- Performance metrics
- Target tracking information

## Performance Optimization

### System Requirements
- CPU: Intel i5 or equivalent
- RAM: 8GB minimum
- GPU: NVIDIA GTX 1060 or better
- Storage: 1GB free space

### Optimization Tips
1. GPU Acceleration
   - Enable CUDA support
   - Use GPU for target detection
   - Optimize memory usage

2. Processing Optimization
   - Reduce processing resolution
   - Implement frame skipping
   - Use efficient algorithms

3. Memory Management
   - Clear unused resources
   - Implement garbage collection
   - Optimize data structures

### Performance Metrics
- Target detection time: < 16ms
- Aim calculation time: < 8ms
- Total latency: < 32ms
- CPU usage: < 30%
- GPU usage: < 50%

## Contributing

### Development Setup
1. Clone repository
2. Install dependencies
3. Set up development environment
4. Run tests

### Code Style
- Follow PEP 8 guidelines
- Use type hints
- Write unit tests
- Document code

### Testing
Run tests using:
```bash
python -m pytest tests/
```

## License
This project is licensed under the MIT License - see the LICENSE file for details. 