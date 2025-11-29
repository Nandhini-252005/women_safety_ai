import cv2
import numpy as np
from ultralytics import YOLO
import mediapipe as mp
import os
from collections import deque, Counter

# --- 1. CONFIGURATION ---
CONF_THRESHOLD = 0.6  # 60% Confidence. (Ignores "ghosts" and background noise)
MIN_BOX_SIZE = 60     # Ignore boxes smaller than 60px (Ignores tiny far-away objects)

# Smoothing Queues (Stabilizes the numbers so they don't flicker)
history_women = deque(maxlen=15)
history_men = deque(maxlen=15)

# --- 2. SETUP MODELS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROTO_PATH = os.path.join(BASE_DIR, "models", "gender_deploy.prototxt")
MODEL_PATH = os.path.join(BASE_DIR, "models", "gender_net.caffemodel")

# Load Gender Model
print("🚀 Loading Gender Classification Model...")
try:
    gender_net = cv2.dnn.readNet(MODEL_PATH, PROTO_PATH)
except cv2.error:
    print("❌ Gender models missing. Please ensure files are in 'models/' folder.")
    gender_net = None

MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)

# Load YOLOv8
try:
    yolo_model = YOLO('yolov8n.pt') 
except:
    yolo_model = YOLO('yolov8n.pt')

# Load MediaPipe (SOS)
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5)

def detect_sos_gesture(frame_rgb):
    results = hands.process(frame_rgb)
    sos_detected = False
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            fingers_up = 0
            if hand_landmarks.landmark[8].y < hand_landmarks.landmark[6].y: fingers_up += 1
            if hand_landmarks.landmark[12].y < hand_landmarks.landmark[10].y: fingers_up += 1
            if hand_landmarks.landmark[16].y < hand_landmarks.landmark[14].y: fingers_up += 1
            if hand_landmarks.landmark[20].y < hand_landmarks.landmark[18].y: fingers_up += 1
            if abs(hand_landmarks.landmark[4].x - hand_landmarks.landmark[3].x) > 0.02: fingers_up += 1

            if fingers_up >= 4:
                sos_detected = True
    return sos_detected

def get_stable_count(queue, current_count):
    """ Returns the most frequent number in the last 15 frames """
    queue.append(current_count)
    return Counter(queue).most_common(1)[0][0]

def run_cv_models(frame):
    raw_women = 0
    raw_men = 0
    sos_flag = False

    # Pre-process
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    h_img, w_img, _ = frame.shape

    # 1. Detect SOS
    sos_flag = detect_sos_gesture(rgb_frame)

    # 2. Detect Persons (Added conf=CONF_THRESHOLD to remove ghosts)
    results = yolo_model(frame, classes=[0], conf=CONF_THRESHOLD, verbose=False) 

    for result in results:
        boxes = result.boxes
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            width = x2 - x1
            height = y2 - y1

            # FILTER: Ignore small background objects
            if width < MIN_BOX_SIZE or height < MIN_BOX_SIZE:
                continue

            # 3. Gender Logic
            padding = 20
            face_x1 = max(0, x1 - padding)
            face_y1 = max(0, y1 - padding)
            face_x2 = min(w_img, x2 + padding)
            face_y2 = min(h_img, y2 + padding)
            
            face_roi = frame[face_y1:face_y2, face_x1:face_x2]

            gender_detected = False

            if face_roi.size > 0 and gender_net is not None:
                try:
                    blob = cv2.dnn.blobFromImage(face_roi, 1.0, (227, 227), MODEL_MEAN_VALUES, swapRB=False)
                    gender_net.setInput(blob)
                    gender_preds = gender_net.forward()
                    
                    female_prob = gender_preds[0][1]
                    male_prob = gender_preds[0][0]
                    
                    # TWEAK: If model is 60% sure it's female, mark female.
                    if female_prob > 0.6:
                        raw_women += 1
                    else:
                        raw_men += 1
                    gender_detected = True
                except:
                    pass
            
            # Fallback if gender detection failed but person exists
            if not gender_detected:
                raw_men += 1

    # 4. STABILIZE COUNTS (Smooths out the flickering)
    stable_women = get_stable_count(history_women, raw_women)
    stable_men = get_stable_count(history_men, raw_men)

    scene_text = f"{stable_women} women, {stable_men} men detected."
    
    return {
        "women": stable_women,
        "men": stable_men,
        "sos": sos_flag,
        "scene": scene_text
    }