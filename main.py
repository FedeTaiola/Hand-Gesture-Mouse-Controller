import cv2
import mediapipe as mp
import pyautogui
import math
import time
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

# dimensioni schermo
screen_w, screen_h = pyautogui.size()

# smoothing mouse
smoothening = 5
prev_x, prev_y = 0, 0

# click cooldown
last_click_time = 0
click_delay = 0.5

# drag & drop (Vision Pro style)
pinch_start_time = None   # quando inizia il pinch
drag_threshold = 0.4      # secondi di pinch per attivare il drag
is_dragging = False       # stiamo trascinando?

# connessioni mano per disegno
HAND_CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,4),
    (0,5),(5,6),(6,7),(7,8),
    (5,9),(9,10),(10,11),(11,12),
    (9,13),(13,14),(14,15),(15,16),
    (13,17),(17,18),(18,19),(19,20),(0,17)
]

# funzione distanza
def distance(p1, p2):
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

def draw_hand(frame, landmarks, h, w):
    pts = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks]
    for a, b in HAND_CONNECTIONS:
        cv2.line(frame, pts[a], pts[b], (200, 200, 200), 1)
    for pt in pts:
        cv2.circle(frame, pt, 4, (255, 255, 255), -1)

# inizializza mediapipe nuovo API
BaseOptions = mp_python.BaseOptions
HandLandmarker = vision.HandLandmarker
HandLandmarkerOptions = vision.HandLandmarkerOptions
VisionRunningMode = vision.RunningMode

import urllib.request, os
model_path = "hand_landmarker.task"
if not os.path.exists(model_path):
    print("Scarico il modello hand_landmarker...")
    urllib.request.urlretrieve(
        "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task",
        model_path
    )
    print("Modello scaricato!")

options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.IMAGE,
    num_hands=1,
    min_hand_detection_confidence=0.7,
    min_tracking_confidence=0.5
)
detector = HandLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0)

while True:

    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
    results = detector.detect(mp_image)

    if results.hand_landmarks:

        for hand_landmarks in results.hand_landmarks:
            h, w, _ = frame.shape
            draw_hand(frame, hand_landmarks, h, w)

            # punta indice
            index_x = int(hand_landmarks[8].x * w)
            index_y = int(hand_landmarks[8].y * h)

            # punta pollice
            thumb_x = int(hand_landmarks[4].x * w)
            thumb_y = int(hand_landmarks[4].y * h)

            # disegna punti
            cv2.circle(frame, (index_x, index_y), 10, (0,255,0), -1)
            cv2.circle(frame, (thumb_x, thumb_y), 10, (255,0,0), -1)

            # coordinate schermo
            screen_x = int(hand_landmarks[8].x * screen_w)
            screen_y = int(hand_landmarks[8].y * screen_h)

            # smoothing movimento mouse
            curr_x = prev_x + (screen_x - prev_x) / smoothening
            curr_y = prev_y + (screen_y - prev_y) / smoothening

            pyautogui.moveTo(curr_x, curr_y)

            prev_x, prev_y = curr_x, curr_y

            # distanza dita
            dist = distance((index_x, index_y), (thumb_x, thumb_y))

            # --- PINCH RILEVATO ---
            if dist < 40:
                current_time = time.time()

                if pinch_start_time is None:
                    pinch_start_time = current_time  # inizia il timer del pinch

                pinch_duration = current_time - pinch_start_time

                if not is_dragging and pinch_duration >= drag_threshold:
                    # pinch tenuto abbastanza: attiva drag
                    pyautogui.mouseDown()
                    is_dragging = True

                if is_dragging:
                    # feedback visivo: cerchio giallo mentre si trascina
                    cv2.circle(frame, (index_x, index_y), 20, (0, 255, 255), 3)
                    cv2.putText(frame, "DRAG", (50, 100),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3)
                else:
                    # pinch breve: mostra barra di caricamento
                    progress = int((pinch_duration / drag_threshold) * 100)
                    bar_w = int((progress / 100) * 200)
                    cv2.rectangle(frame, (50, 110), (250, 130), (50, 50, 50), -1)
                    cv2.rectangle(frame, (50, 110), (50 + bar_w, 130), (0, 255, 255), -1)
                    cv2.putText(frame, "Tieni per drag...", (50, 105),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

            # --- PINCH RILASCIATO ---
            else:
                if is_dragging:
                    # rilascia il mouse (drop)
                    pyautogui.mouseUp()
                    is_dragging = False

                elif pinch_start_time is not None:
                    # era un pinch breve: esegui click normale
                    current_time = time.time()
                    if current_time - last_click_time > click_delay:
                        pyautogui.click()
                        last_click_time = current_time
                        cv2.putText(frame, "CLICK", (50, 100),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

                pinch_start_time = None  # reset timer

    # HUD overlay
    cv2.rectangle(frame,(10,10),(300,90),(0,0,0),-1)

    cv2.putText(frame, "HAND MOUSE", (20,40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
    cv2.putText(frame, "Index = Move | Pinch = Click", (20,65),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
    cv2.putText(frame, "Pinch long = DRAG", (20,85),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,255), 1)

    cv2.imshow("Hand Gesture Mouse Controller", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()