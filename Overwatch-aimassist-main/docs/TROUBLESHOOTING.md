# Troubleshooting Guide

This guide provides solutions for common issues you might encounter while using Overwatch Aim Assist.

## Performance Issues

### High CPU Usage

**Symptoms:**
- System becomes sluggish
- High CPU usage in Task Manager
- Frame drops in game

**Solutions:**
1. Enable GPU acceleration:
   ```json
   {
       "performance": {
           "use_gpu": true
       }
   }
   ```
2. Reduce processing resolution:
   ```json
   {
       "performance": {
           "processing_resolution": 0.75
       }
   }
   ```
3. Increase frame skip:
   ```json
   {
       "performance": {
           "frame_skip": 1
       }
   }
   ```

### High Memory Usage

**Symptoms:**
- Memory usage increases over time
- System becomes unresponsive
- Application crashes

**Solutions:**
1. Clear cache:
   ```bash
   python src/utils/cache_manager.py clear
   ```
2. Reduce target detection frequency:
   ```json
   {
       "target_detection": {
           "detection_frequency": 30
       }
   }
   ```
3. Enable memory optimization:
   ```json
   {
       "performance": {
           "optimize_memory": true
       }
   }
   ```

## Detection Issues

### False Positives

**Symptoms:**
- Assistant targets incorrect objects
- Random targeting
- Inconsistent detection

**Solutions:**
1. Adjust confidence threshold:
   ```json
   {
       "target_detection": {
           "confidence_threshold": 0.8
       }
   }
   ```
2. Update target detection model:
   ```bash
   python src/utils/model_updater.py update
   ```
3. Calibrate detection:
   ```bash
   python src/utils/calibration.py run
   ```

### Missed Targets

**Symptoms:**
- Targets not detected
- Inconsistent detection
- Delayed detection

**Solutions:**
1. Lower confidence threshold:
   ```json
   {
       "target_detection": {
           "confidence_threshold": 0.6
       }
   }
   ```
2. Adjust minimum target size:
   ```json
   {
       "target_detection": {
           "min_target_size": 15
       }
   }
   ```
3. Check lighting conditions

## Aim Assistance Issues

### Erratic Movement

**Symptoms:**
- Unpredictable aim movement
- Jerky crosshair movement
- Over-correction

**Solutions:**
1. Adjust smoothing factor:
   ```json
   {
       "aim_assistance": {
           "smoothing_factor": 0.7
       }
   }
   ```
2. Reduce sensitivity:
   ```json
   {
       "sensitivity": {
           "base": 0.8
       }
   }
   ```
3. Disable prediction:
   ```json
   {
       "aim_assistance": {
           "enable_prediction": false
       }
   }
   ```

### Delayed Response

**Symptoms:**
- Lag between detection and movement
- Slow aim adjustment
- Delayed target tracking

**Solutions:**
1. Reduce processing resolution
2. Enable frame skipping
3. Optimize target detection frequency

## Configuration Issues

### Settings Not Saving

**Symptoms:**
- Changes not persisting
- Settings reset on restart
- Profile issues

**Solutions:**
1. Check file permissions
2. Verify config file location
3. Use profile manager:
   ```bash
   python src/utils/profile_manager.py save "My Profile"
   ```

### Invalid Configuration

**Symptoms:**
- Application crashes on start
- Settings not applying
- Error messages

**Solutions:**
1. Reset to default:
   ```bash
   python src/utils/config_manager.py reset
   ```
2. Validate configuration:
   ```bash
   python src/utils/config_manager.py validate
   ```
3. Check config file format

## Game Integration Issues

### Not Detecting Game

**Symptoms:**
- Assistant not starting
- No target detection
- Game window not found

**Solutions:**
1. Verify game is running
2. Check window mode (Borderless recommended)
3. Run as administrator

### Performance Impact

**Symptoms:**
- Game FPS drops
- Input lag
- System slowdown

**Solutions:**
1. Enable performance mode
2. Reduce processing load
3. Optimize settings

## Getting Help

If you're still experiencing issues:

1. Check the [Documentation](README.md)
2. Search [GitHub Issues](https://github.com/Echosvoid/Overwatch-aimassist/issues)
3. Join our [Discord Server](https://discord.gg/overwatch-aimassist)
4. Contact support

## Reporting Issues

When reporting an issue, please include:

1. System specifications
2. Error messages
3. Steps to reproduce
4. Expected vs actual behavior
5. Screenshots/videos if applicable 