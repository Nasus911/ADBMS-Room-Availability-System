import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import os

# Get script directory
script_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(script_dir, 'hand_landmarker.task')

# Setup MediaPipe Hand Landmarker
base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=2,
    min_hand_detection_confidence=0.7,
    min_hand_presence_confidence=0.7,
    min_tracking_confidence=0.7)
detector = vision.HandLandmarker.create_from_options(options)

# Capture video
cap = cv2.VideoCapture(0)

# Finger tip landmark indices
finger_tips = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky

# Connection indices for drawing
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),  # Thumb
    (0, 5), (5, 6), (6, 7), (7, 8),  # Index
    (0, 9), (9, 10), (10, 11), (11, 12),  # Middle
    (0, 13), (13, 14), (14, 15), (15, 16),  # Ring
    (0, 17), (17, 18), (18, 19), (19, 20),  # Pinky
    (5, 9), (9, 13), (13, 17)  # Palm
]

print("Hand Tracker Started! Press 'q' to quit.")
print("Show your hand to the camera.")

while True:
    success, img = cap.read()
    if not success:
        print("Failed to capture video")
        break
    
    # Flip the image horizontally to mirror it (natural camera view)
    img = cv2.flip(img, 1)
    
    # Convert to RGB for MediaPipe
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
    
    # Detect hands
    detection_result = detector.detect(mp_image)
    
    # Draw landmarks and gestures
    if detection_result.hand_landmarks:
        for hand_landmarks in detection_result.hand_landmarks:
            h, w, c = img.shape
            landmarks = []
            
            # Draw landmarks
            for lm in hand_landmarks:
                cx, cy = int(lm.x * w), int(lm.y * h)
                landmarks.append((cx, cy))
                cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
            
            # Draw connections
            for connection in HAND_CONNECTIONS:
                start_idx, end_idx = connection
                start_point = landmarks[start_idx]
                end_point = landmarks[end_idx]
                cv2.line(img, start_point, end_point, (0, 255, 0), 2)
            
            # Gesture detection
            fingers_up = []
            
            # Thumb: check if tip is to the right of joint (for right hand)
            if landmarks[finger_tips[0]][0] > landmarks[finger_tips[0] - 1][0]:
                fingers_up.append(1)
            else:
                fingers_up.append(0)
            
            # Other fingers: tip higher (smaller y) than joint
            for tip in finger_tips[1:]:
                if landmarks[tip][1] < landmarks[tip - 2][1]:
                    fingers_up.append(1)
                else:
                    fingers_up.append(0)
            
            # Count fingers
            total_fingers = sum(fingers_up)

            # Prepare finger name list and active fingers string
            finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
            active_fingers = [finger_names[i] for i, v in enumerate(fingers_up) if v]
            active_str = ', '.join(active_fingers) if active_fingers else 'None'

            # Shutdown on single middle finger up
            # fingers_up order: [thumb, index, middle, ring, pinky]
            is_middle_only = (fingers_up == [0, 0, 1, 0, 0])

            if is_middle_only:
                cv2.putText(img, "MIDDLE FINGER DETECTED - SHUTTING DOWN!", (30, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                cv2.putText(img, f"Raised: {active_str}", (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,0,255), 2)
                cv2.imshow("Finger Tracking + Gestures", img)
                cv2.waitKey(1500)
                break
            elif total_fingers == 1 and fingers_up[0] == 1:
                cv2.putText(img, "Thumbs Up!", (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
                cv2.putText(img, f"Raised: {active_str}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)
            else:
                cv2.putText(img, f"Fingers: {total_fingers}", (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)
                cv2.putText(img, f"Raised: {active_str}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255,0,0), 2)
    
    cv2.imshow("Finger Tracking + Gestures", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("Hand Tracker Stopped.")