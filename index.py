import cv2
import time
import numpy as np

# Constants for face detection
SCALE_FACTOR = 1.1  # Lower = more thorough (slower but more sensitive)
MIN_NEIGHBORS = 3  # Lower = more detections (may have false positives)
MIN_FACE_SIZE = (30, 30)  # Minimum face size to detect
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Movement detection thresholds
MOVEMENT_THRESHOLD = 5  # Minimum pixels to register as movement
DIAGONAL_RATIO = 0.6  # Ratio for diagonal detection
SMOOTHING_FACTOR = 0.7  # Exponential smoothing (0-1, higher = more smoothing)

# Load Haar Cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

# Initialize camera
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("[ERROR] Cannot access camera.")
    exit(1)

# Set camera resolution
cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

# Variables for tracking
prev_center = None
prev_time = time.time()
direction = "Center"
speed = 0.0
smoothed_speed = 0.0
head_pose = "Frontal"
distance = 0.0

print("[INFO] Starting Face Direction Tracker (OpenCV only)...")
print("[INFO] Press 'q' to quit")

while True:
    ret, frame = cap.read()
    if not ret:
        print("[ERROR] Failed to capture frame from camera.")
        break

    # Flip frame horizontally (mirror effect)
    frame = cv2.flip(frame, 1)

    # Convert to grayscale for face detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Apply histogram equalization for better contrast
    gray = cv2.equalizeHist(gray)
    
    # Apply Gaussian blur to reduce noise
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Detect faces with improved parameters
    faces = face_cascade.detectMultiScale(
        gray, 
        scaleFactor=SCALE_FACTOR,
        minNeighbors=MIN_NEIGHBORS,
        minSize=MIN_FACE_SIZE,
        flags=cv2.CASCADE_SCALE_IMAGE
    )

    if len(faces) > 0:
        # Use the largest face detected
        face = max(faces, key=lambda rect: rect[2] * rect[3])
        x, y, w, h = face
        
        # Draw bounding box
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Calculate center
        cx, cy = x + w // 2, y + h // 2
        cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)
        
        # Detect eyes for head pose estimation
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = frame[y:y+h, x:x+w]
        eyes = eye_cascade.detectMultiScale(roi_gray, 1.1, 5)
        
        # Draw eyes
        for (ex, ey, ew, eh) in eyes:
            cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (255, 0, 255), 2)
        
        # Estimate head pose based on eye positions
        if len(eyes) >= 2:
            # Sort eyes by x position
            eyes_sorted = sorted(eyes, key=lambda e: e[0])
            left_eye = eyes_sorted[0]
            right_eye = eyes_sorted[1]
            
            # Calculate eye center
            left_eye_center = left_eye[0] + left_eye[2] // 2
            right_eye_center = right_eye[0] + right_eye[2] // 2
            eye_center_x = (left_eye_center + right_eye_center) // 2
            
            # Face center relative to bounding box
            face_center_x = w // 2
            horizontal_offset = eye_center_x - face_center_x
            
            # Determine head pose
            if abs(horizontal_offset) < 15:
                head_pose = "Frontal"
            elif horizontal_offset > 15:
                head_pose = "Turned Right"
            else:
                head_pose = "Turned Left"
        elif len(eyes) == 1:
            # Only one eye visible - face is turned
            eye_x = eyes[0][0] + eyes[0][2] // 2
            if eye_x < w // 3:
                head_pose = "Turned Left"
            elif eye_x > 2 * w // 3:
                head_pose = "Turned Right"
            else:
                head_pose = "Frontal"
        else:
            head_pose = "Unknown"

        current_time = time.time()
        dt = current_time - prev_time if prev_time else 0.0001

        if prev_center:
            dx = cx - prev_center[0]
            dy = cy - prev_center[1]
            
            # Calculate distance and speed
            distance = (dx**2 + dy**2)**0.5
            speed = distance / dt
            
            # Apply exponential smoothing to speed
            smoothed_speed = (SMOOTHING_FACTOR * smoothed_speed + 
                            (1 - SMOOTHING_FACTOR) * speed)
            
            # Determine direction with threshold and diagonal support
            if distance < MOVEMENT_THRESHOLD:
                direction = "Center"
            else:
                abs_dx = abs(dx)
                abs_dy = abs(dy)
                
                # Check for diagonal movement
                if abs_dx > 0 and abs_dy > 0:
                    ratio = min(abs_dx, abs_dy) / max(abs_dx, abs_dy)
                    
                    if ratio >= DIAGONAL_RATIO:
                        # Diagonal movement
                        if dx > 0 and dy > 0:
                            direction = "Down-Right"
                        elif dx > 0 and dy < 0:
                            direction = "Up-Right"
                        elif dx < 0 and dy > 0:
                            direction = "Down-Left"
                        else:
                            direction = "Up-Left"
                    else:
                        # Predominantly one direction
                        if abs_dx > abs_dy:
                            direction = "Right" if dx > 0 else "Left"
                        else:
                            direction = "Down" if dy > 0 else "Up"
                else:
                    # Pure horizontal or vertical
                    if abs_dx > abs_dy:
                        direction = "Right" if dx > 0 else "Left"
                    else:
                        direction = "Down" if dy > 0 else "Up"

        prev_center = (cx, cy)
        prev_time = current_time

        # Display information
        cv2.putText(frame, f"Direction: {direction}", (20, 40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(frame, f"Speed: {smoothed_speed:.2f}px/s", (20, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        cv2.putText(frame, f"Head Pose: {head_pose}", (20, 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 100, 255), 2)
        cv2.putText(frame, f"Eyes Detected: {len(eyes)}", (20, 130), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 255, 100), 2)
        
        # Draw movement vector
        if prev_center and distance >= MOVEMENT_THRESHOLD:
            cv2.arrowedLine(frame, prev_center, (cx, cy), (0, 255, 255), 2, tipLength=0.3)
    else:
        # No faces detected, reset tracking
        direction = "Center"
        speed = 0.0
        smoothed_speed = 0.0
        prev_center = None
        head_pose = "Unknown"
        cv2.putText(frame, "No Face Detected", (20, 40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    # Display FPS
    fps = 1.0 / (time.time() - prev_time) if prev_time else 0
    cv2.putText(frame, f"FPS: {fps:.1f}", (FRAME_WIDTH - 120, 30), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    cv2.imshow("Face Direction Tracker (OpenCV)", frame)

    # Exit on 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("[INFO] Exiting...")
        break

cap.release()
cv2.destroyAllWindows()
