/*
 * Face Tracking Stepper Motor Control - Angle Based
 * 
 * This Arduino sketch controls a stepper motor via a motor driver (e.g., A4988, DRV8825)
 * based on angle commands received from the Python face tracking script.
 * 
 * Hardware Setup:
 * - Arduino Uno
 * - Stepper Motor (e.g., NEMA 17)
 * - Motor Driver (A4988 or DRV8825)
 * - Power Supply (12V recommended for motor)
 * 
 * Connections:
 * - DIR (Direction) -> Pin 2
 * - STEP (Step) -> Pin 3
 * - ENABLE -> Pin 4 (optional)
 * - Motor Driver to Stepper Motor (A+, A-, B+, B-)
 * - Motor Driver VMOT to 12V Power Supply
 * - Motor Driver GND to Arduino GND and Power Supply GND
 * 
 * Commands from Python:
 * - "-10" -> Rotate -10 degrees (counter-clockwise)
 * - "45" -> Rotate 45 degrees (clockwise)
 * - Any integer angle value
 */

// Pin definitions
const int DIR_PIN = 2;      // Direction pin
const int STEP_PIN = 3;     // Step pin
const int ENABLE_PIN = 4;   // Enable pin (LOW = enabled, HIGH = disabled)

// Motor parameters
const int STEPS_PER_REV = 200;      // Steps per revolution (1.8° per step)
const int MICROSTEPS = 1;           // Microstepping (1, 2, 4, 8, 16)
const int STEP_DELAY = 1000;        // Microseconds between steps (lower = faster)

// Motor state
bool motorEnabled = false;

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  
  // Set pin modes
  pinMode(DIR_PIN, OUTPUT);
  pinMode(STEP_PIN, OUTPUT);
  pinMode(ENABLE_PIN, OUTPUT);
  
  // Disable motor initially
  digitalWrite(ENABLE_PIN, HIGH);
  
  // Initialize pins
  digitalWrite(DIR_PIN, LOW);
  digitalWrite(STEP_PIN, LOW);
  
  Serial.println("[ARDUINO] Stepper Motor Angle Controller Ready");
  Serial.println("[ARDUINO] Waiting for angle commands...");
  
  // Visual feedback - blink built-in LED
  pinMode(LED_BUILTIN, OUTPUT);
  for (int i = 0; i < 3; i++) {
    digitalWrite(LED_BUILTIN, HIGH);
    delay(200);
    digitalWrite(LED_BUILTIN, LOW);
    delay(200);
  }
}

void loop() {
  // Check for incoming serial commands
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();  // Remove whitespace
    
    if (command.length() > 0) {
      // Convert string to integer angle
      int angle = command.toInt();
      
      if (angle != 0 || command == "0") {
        Serial.print("[ARDUINO] Received angle: ");
        Serial.print(angle);
        Serial.println("°");
        
        // Rotate by the specified angle
        rotateByAngle(angle);
      } else {
        Serial.println("[ARDUINO] Invalid angle received");
      }
    }
  }
  
  // Small delay to prevent overwhelming the Arduino
  delay(10);
}

void enableMotor() {
  if (!motorEnabled) {
    digitalWrite(ENABLE_PIN, LOW);  // Enable motor (active LOW)
    motorEnabled = true;
    digitalWrite(LED_BUILTIN, HIGH);
    delay(10);  // Small delay for driver to enable
  }
}

void disableMotor() {
  if (motorEnabled) {
    digitalWrite(ENABLE_PIN, HIGH);  // Disable motor (active LOW)
    motorEnabled = false;
    digitalWrite(LED_BUILTIN, LOW);
  }
}

void rotateByAngle(int angle) {
  // Calculate number of steps needed
  // Steps = (angle / 360) * STEPS_PER_REV * MICROSTEPS
  long steps = (long)abs(angle) * STEPS_PER_REV * MICROSTEPS / 360;
  
  if (steps == 0) {
    return;  // No rotation needed
  }
  
  enableMotor();
  
  // Set direction based on angle sign
  if (angle > 0) {
    digitalWrite(DIR_PIN, HIGH);  // Clockwise
    Serial.println("[ARDUINO] Rotating clockwise");
  } else {
    digitalWrite(DIR_PIN, LOW);   // Counter-clockwise
    Serial.println("[ARDUINO] Rotating counter-clockwise");
  }
  
  // Perform the rotation
  for (long i = 0; i < steps; i++) {
    digitalWrite(STEP_PIN, HIGH);
    delayMicroseconds(STEP_DELAY);
    digitalWrite(STEP_PIN, LOW);
    delayMicroseconds(STEP_DELAY);
  }
  
  Serial.print("[ARDUINO] Rotation complete: ");
  Serial.print(steps);
  Serial.println(" steps");
  
  // Keep motor enabled for a short time after rotation
  delay(100);
  disableMotor();
}

/*
 * Alternative function for smoother acceleration/deceleration
 * Uncomment to use instead of the simple rotation
 */
/*
void rotateByAngleSmooth(int angle) {
  long steps = (long)abs(angle) * STEPS_PER_REV * MICROSTEPS / 360;
  
  if (steps == 0) {
    return;
  }
  
  enableMotor();
  
  if (angle > 0) {
    digitalWrite(DIR_PIN, HIGH);
  } else {
    digitalWrite(DIR_PIN, LOW);
  }
  
  int maxSpeed = STEP_DELAY;
  int minSpeed = STEP_DELAY * 3;
  int accelSteps = min(steps / 4, 20);
  
  for (long i = 0; i < steps; i++) {
    int currentDelay;
    
    // Acceleration
    if (i < accelSteps) {
      currentDelay = map(i, 0, accelSteps, minSpeed, maxSpeed);
    }
    // Deceleration
    else if (i > steps - accelSteps) {
      currentDelay = map(i, steps - accelSteps, steps, maxSpeed, minSpeed);
    }
    // Constant speed
    else {
      currentDelay = maxSpeed;
    }
    
    digitalWrite(STEP_PIN, HIGH);
    delayMicroseconds(currentDelay);
    digitalWrite(STEP_PIN, LOW);
    delayMicroseconds(currentDelay);
  }
  
  delay(100);
  disableMotor();
}
*/
