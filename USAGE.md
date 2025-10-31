# Face Direction Tracker - Usage Guide

## Quick Start

### Phase 1: Face Detection Only
Run basic face tracking without motor control:
```bash
# This was your original Phase 1 (now in index.py with motor control)
```

### Phase 2: Face Tracking with Motor Control

#### Option 1: Using `index.py` (Angle-Based Control)
This sends specific rotation angles based on face position:
- **Face moves LEFT** → Send `-10°` to Arduino
- **Face moves RIGHT** → Send `45°` to Arduino
- **Face in CENTER** (dead zone) → No rotation

```bash
python3 index.py
```

**Features:**
- Dead zone: 100px from center (configurable)
- Left rotation: -10 degrees
- Right rotation: 45 degrees
- Visual feedback with center line and dead zone overlay
- Shows offset, motor command, and rotation angle on screen

#### Option 2: Using `face_tracker_with_motor.py` (Command-Based Control)
This sends text commands (LEFT, RIGHT, STOP) to Arduino:

```bash
python3 face_tracker_with_motor.py
```

**Features:**
- Dead zone: 100px from center
- Continuous rotation while face is outside dead zone
- Text-based commands for simpler Arduino code

## Arduino Sketches

### For `index.py` - Use `stepper_motor_angle_control.ino`
Receives angle values and rotates accordingly:
```cpp
// Receives: "-10" or "45"
// Calculates steps and rotates by that angle
```

### For `face_tracker_with_motor.py` - Use `stepper_motor_control.ino`
Receives text commands:
```cpp
// Receives: "LEFT", "RIGHT", "STOP", "CENTER"
// Rotates continuously in specified direction
```

## Configuration

### Adjusting Rotation Angles (in `index.py`)
```python
LEFT_ROTATION = -10   # Change this for different left rotation
RIGHT_ROTATION = 45   # Change this for different right rotation
DEAD_ZONE = 100       # Change this for larger/smaller center zone
```

### Adjusting Motor Speed (in Arduino)
```cpp
const int STEP_DELAY = 1000;  // Lower = faster (microseconds)
```

### Adjusting Detection Sensitivity
```python
SCALE_FACTOR = 1.1     # Lower = more sensitive (slower)
MIN_NEIGHBORS = 3      # Lower = more detections
DEAD_ZONE = 100        # Pixels from center before motor activates
```

## Visual Indicators

### On Screen Display
- **Green box**: Detected face
- **Blue dot**: Face center
- **Gray vertical line**: Frame center
- **Gray rectangle**: Dead zone (motor won't move here)
- **Yellow line**: Line from center to face
- **Offset**: Horizontal distance from center in pixels
- **Motor**: Current command and rotation angle
- **Status**: "Connected" (green) or "Simulation" (red)

### Arduino LED
- **Blinking**: Motor is active
- **Off**: Motor is idle

## Troubleshooting

### "Arduino not found. Running in simulation mode"
- Check USB connection
- Verify Arduino is powered
- Check port permissions:
  ```bash
  sudo usermod -a -G dialout $USER
  # Log out and log back in
  ```

### Motor rotates wrong direction
Swap the rotation angles:
```python
LEFT_ROTATION = 45    # Swap these
RIGHT_ROTATION = -10  # values
```

Or in Arduino, swap DIR pin logic:
```cpp
// In rotateByAngle() function
if (angle > 0) {
    digitalWrite(DIR_PIN, LOW);   // Swap HIGH to LOW
} else {
    digitalWrite(DIR_PIN, HIGH);  // Swap LOW to HIGH
}
```

### Face detection not working
1. Improve lighting
2. Move closer to camera
3. Adjust parameters:
```python
SCALE_FACTOR = 1.05  # More sensitive
MIN_NEIGHBORS = 2    # More lenient
```

### Motor too fast/slow
In Arduino code:
```cpp
const int STEP_DELAY = 2000;  // Increase for slower
const int STEP_DELAY = 500;   // Decrease for faster
```

## Command Line Options

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run with Virtual Environment
```bash
source venv/bin/activate
python3 index.py
```

### Exit Program
Press **'q'** key in the video window

## Serial Monitor (Arduino IDE)

To see what Arduino is receiving:
1. Open Arduino IDE
2. Tools → Serial Monitor
3. Set baud rate to 9600
4. You'll see:
```
[ARDUINO] Stepper Motor Angle Controller Ready
[ARDUINO] Waiting for angle commands...
[ARDUINO] Received angle: -10°
[ARDUINO] Rotating counter-clockwise
[ARDUINO] Rotation complete: 5 steps
```

## Tips for Demo

1. **Good lighting** - Face detection works best with even lighting
2. **Clear background** - Reduces false detections
3. **Center yourself** - Start in the dead zone, then move left/right
4. **Attach indicator** - Put a stick/cardboard on motor shaft to show rotation
5. **Show serial monitor** - Demonstrates Arduino communication
6. **Explain dead zone** - Show how motor only moves when you leave center

## Next Steps (Phase 3)

- Mount USB camera on motor
- Add vertical axis (second motor)
- Implement PID control for smooth tracking
- Add auto-centering feature
- Create 3D-printed camera mount
